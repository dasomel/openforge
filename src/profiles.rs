use crate::policy::{Policy, Profile};
use anyhow::{Result, bail};

fn profile(name: &str, include_rules: &[&str], exclude_rules: &[&str]) -> Policy {
    Policy {
        profile: Profile {
            name: name.to_string(),
            include_rules: include_rules
                .iter()
                .map(|value| (*value).to_string())
                .collect(),
            exclude_rules: exclude_rules
                .iter()
                .map(|value| (*value).to_string())
                .collect(),
        },
        waivers: Vec::new(),
    }
}

pub(crate) fn builtin(name: &str) -> Result<Policy> {
    match name {
        "production" => Ok(profile("production", &[], &[])),
        "kubernetes-platform" => Ok(profile(
            "kubernetes-platform",
            &[
                "DOC-*", "GOV-*", "SEC-*", "CI-*", "REL-*", "PLT-*", "WEB-*", "EXE-*",
                "RT-*",
            ],
            &[],
        )),
        "oss-library" => Ok(profile(
            "oss-library",
            &[
                "DOC-*", "GOV-*", "SEC-*", "CI-*", "REL-*", "WEB-*", "EXE-*",
            ],
            &[],
        )),
        "repository" => Ok(profile(
            "repository",
            &[
                "DOC-*", "GOV-*", "SEC-*", "CI-*", "REL-*", "PLT-*", "WEB-*", "EXE-*",
            ],
            &[],
        )),
        other => bail!(
            "unknown built-in profile '{other}'; supported profiles: production, kubernetes-platform, oss-library, repository"
        ),
    }
}

pub(crate) fn overlay(mut base: Policy, override_policy: Policy) -> Policy {
    if override_policy.profile.name != "default" {
        base.profile.name = override_policy.profile.name;
    }
    if !override_policy.profile.include_rules.is_empty() {
        base.profile.include_rules = override_policy.profile.include_rules;
    }
    if !override_policy.profile.exclude_rules.is_empty() {
        base.profile.exclude_rules = override_policy.profile.exclude_rules;
    }
    base.waivers.extend(override_policy.waivers);
    base
}

#[cfg(test)]
mod tests {
    use super::{builtin, overlay};
    use crate::policy::{Policy, Profile, Waiver};

    #[test]
    fn oss_library_excludes_runtime_by_inclusion_scope() {
        let policy = builtin("oss-library").unwrap();
        assert!(policy.profile.include_rules.contains(&"DOC-*".to_string()));
        assert!(policy.profile.include_rules.contains(&"WEB-*".to_string()));
        assert!(!policy.profile.include_rules.contains(&"RT-*".to_string()));
    }

    #[test]
    fn explicit_policy_overrides_profile_scope_and_adds_waivers() {
        let base = builtin("kubernetes-platform").unwrap();
        let override_policy = Policy {
            profile: Profile {
                name: "edge-platform".to_string(),
                include_rules: vec!["RT-*".to_string()],
                exclude_rules: vec!["RT-021".to_string()],
            },
            waivers: vec![Waiver {
                rule_id: "RT-005".to_string(),
                reason: "single-node edge profile".to_string(),
                expires: "2026-12-31".to_string(),
            }],
        };
        let merged = overlay(base, override_policy);
        assert_eq!(merged.profile.name, "edge-platform");
        assert_eq!(merged.profile.include_rules, vec!["RT-*".to_string()]);
        assert_eq!(merged.profile.exclude_rules, vec!["RT-021".to_string()]);
        assert_eq!(merged.waivers.len(), 1);
    }
}
