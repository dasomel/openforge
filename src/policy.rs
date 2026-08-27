use crate::Finding;
use anyhow::{Context, Result};
use chrono::{NaiveDate, Utc};
use globset::{Glob, GlobSet, GlobSetBuilder};
use serde::{Deserialize, Serialize};
use std::{fs, path::Path};

#[derive(Debug, Deserialize)]
pub(crate) struct Policy {
    #[serde(default)]
    pub(crate) profile: Profile,
    #[serde(default)]
    pub(crate) waivers: Vec<Waiver>,
}

#[derive(Debug, Default, Deserialize)]
pub(crate) struct Profile {
    #[serde(default = "default_profile_name")]
    pub(crate) name: String,
    #[serde(default)]
    pub(crate) include_rules: Vec<String>,
    #[serde(default)]
    pub(crate) exclude_rules: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct Waiver {
    pub(crate) rule_id: String,
    pub(crate) reason: String,
    pub(crate) expires: String,
}

#[derive(Debug, Serialize)]
pub(crate) struct PolicySummary {
    pub(crate) profile: String,
    pub(crate) not_applicable: usize,
    pub(crate) waived: usize,
    pub(crate) expired_waivers: usize,
    pub(crate) invalid_waivers: usize,
}

fn default_profile_name() -> String {
    "default".to_string()
}

pub(crate) fn load(path: &Path) -> Result<Policy> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("cannot read policy: {}", path.display()))?;
    serde_json::from_str(&text).with_context(|| format!("invalid policy JSON: {}", path.display()))
}

fn compile_globs(patterns: &[String]) -> Result<Option<GlobSet>> {
    if patterns.is_empty() {
        return Ok(None);
    }
    let mut builder = GlobSetBuilder::new();
    for pattern in patterns {
        builder.add(
            Glob::new(pattern).with_context(|| format!("invalid policy rule glob: {pattern}"))?,
        );
    }
    Ok(Some(builder.build()?))
}

fn applicable(rule_id: &str, include: Option<&GlobSet>, exclude: Option<&GlobSet>) -> bool {
    let included = include.is_none_or(|set| set.is_match(rule_id));
    let excluded = exclude.is_some_and(|set| set.is_match(rule_id));
    included && !excluded
}

pub(crate) fn apply(findings: &mut [Finding], policy: &Policy) -> Result<PolicySummary> {
    let include = compile_globs(&policy.profile.include_rules)?;
    let exclude = compile_globs(&policy.profile.exclude_rules)?;
    let today = Utc::now().date_naive();

    let mut summary = PolicySummary {
        profile: policy.profile.name.clone(),
        not_applicable: 0,
        waived: 0,
        expired_waivers: 0,
        invalid_waivers: 0,
    };

    for finding in findings.iter_mut() {
        if !applicable(&finding.rule_id, include.as_ref(), exclude.as_ref()) {
            finding.status = "NOT_APPLICABLE";
            finding.evidence.push(format!(
                "profile={} applicability=excluded",
                policy.profile.name
            ));
            summary.not_applicable += 1;
            continue;
        }

        let Some(waiver) = policy
            .waivers
            .iter()
            .find(|waiver| waiver.rule_id == finding.rule_id)
        else {
            continue;
        };

        if finding.status == "SKIP" {
            continue;
        }
        if waiver.reason.trim().is_empty() {
            finding
                .evidence
                .push("waiver_ignored=empty_reason".to_string());
            summary.invalid_waivers += 1;
            continue;
        }

        let expires = match NaiveDate::parse_from_str(&waiver.expires, "%Y-%m-%d") {
            Ok(date) => date,
            Err(_) => {
                finding.evidence.push(format!(
                    "waiver_ignored=invalid_expiry expiry={}",
                    waiver.expires
                ));
                summary.invalid_waivers += 1;
                continue;
            }
        };

        if expires < today {
            finding.evidence.push(format!(
                "waiver_expired={} reason={}",
                waiver.expires, waiver.reason
            ));
            summary.expired_waivers += 1;
            continue;
        }

        finding.status = "WAIVED";
        finding.evidence.push(format!(
            "waiver_expires={} reason={}",
            waiver.expires, waiver.reason
        ));
        summary.waived += 1;
    }

    Ok(summary)
}

#[cfg(test)]
mod tests {
    use super::{applicable, compile_globs};

    #[test]
    fn profile_include_and_exclude_rules_are_deterministic() {
        let include = compile_globs(&["RT-*".to_string()]).unwrap().unwrap();
        let exclude = compile_globs(&["RT-021".to_string()]).unwrap().unwrap();
        assert!(applicable("RT-020", Some(&include), Some(&exclude)));
        assert!(!applicable("RT-021", Some(&include), Some(&exclude)));
        assert!(!applicable("DOC-001", Some(&include), Some(&exclude)));
    }
}
