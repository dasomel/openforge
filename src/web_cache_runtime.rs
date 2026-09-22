use crate::Finding;
use reqwest::{
    blocking::Client,
    header::{AGE, CACHE_CONTROL, ETAG, LAST_MODIFIED},
    redirect::Policy,
};
use std::time::Duration;

const WEIGHT: f64 = 6.0;

fn max_age_seconds(cache_control: &str) -> Option<u64> {
    cache_control.split(',').find_map(|part| {
        let part = part.trim();
        let value = part
            .strip_prefix("max-age=")
            .or_else(|| part.strip_prefix("s-maxage="))?;
        value.trim_matches('"').parse().ok()
    })
}

fn cache_policy_passes(cache_control: Option<&str>) -> bool {
    let Some(cache_control) = cache_control else {
        return false;
    };
    let lower = cache_control.to_ascii_lowercase();
    lower.contains("immutable") && max_age_seconds(&lower).is_some_and(|seconds| seconds >= 86_400)
}

fn validate_url(url: &str) -> Result<(), &'static str> {
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return Err("web cache URL must use http:// or https://");
    }
    if url.contains('@') {
        return Err("web cache URL must not contain userinfo credentials");
    }
    Ok(())
}

pub(crate) fn finding(url: Option<&str>) -> Finding {
    let Some(url) = url else {
        return Finding {
            rule_id: "WEB-008".to_string(),
            category: "Web Assets".to_string(),
            title: "Runtime image endpoint returns immutable cache headers".to_string(),
            status: "SKIP",
            score: 0.0,
            weight: 0.0,
            evidence: vec!["no explicit --web-cache-url provided".to_string()],
            remediation: String::new(),
        };
    };

    if let Err(reason) = validate_url(url) {
        return failed(vec![format!("probe_error={reason}")]);
    }

    let client = match Client::builder()
        .connect_timeout(Duration::from_secs(5))
        .timeout(Duration::from_secs(10))
        .redirect(Policy::none())
        .build()
    {
        Ok(client) => client,
        Err(_) => {
            return failed(vec![
                "probe_error=http_client_initialization_failed".to_string(),
            ]);
        }
    };

    let response = match client.head(url).send() {
        Ok(response) => response,
        Err(_) => return failed(vec!["probe_error=head_request_failed".to_string()]),
    };

    let status = response.status();
    if !status.is_success() {
        return failed(vec![format!("http_status={}", status.as_u16())]);
    }

    let headers = response.headers();
    let cache_control = headers
        .get(CACHE_CONTROL)
        .and_then(|value| value.to_str().ok());
    let passed = cache_policy_passes(cache_control);
    let mut evidence = vec![format!("http_status={}", status.as_u16())];
    match cache_control {
        Some(value) => evidence.push(format!("cache-control={value}")),
        None => evidence.push("cache-control=missing".to_string()),
    }
    for (name, header) in [
        ("age", AGE),
        ("etag", ETAG),
        ("last-modified", LAST_MODIFIED),
    ] {
        if let Some(value) = headers.get(header).and_then(|value| value.to_str().ok()) {
            evidence.push(format!("{name}={value}"));
        }
    }

    Finding {
        rule_id: "WEB-008".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime image endpoint returns immutable cache headers".to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { WEIGHT } else { 0.0 },
        weight: WEIGHT,
        evidence,
        remediation: "Serve the explicit image endpoint with Cache-Control containing immutable and a max-age or s-maxage of at least 86400 seconds.".to_string(),
    }
}

fn failed(evidence: Vec<String>) -> Finding {
    Finding {
        rule_id: "WEB-008".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime image endpoint returns immutable cache headers".to_string(),
        status: "FAIL",
        score: 0.0,
        weight: WEIGHT,
        evidence,
        remediation: "Provide a reachable explicit HTTP(S) image URL and ensure it returns long-lived immutable Cache-Control headers.".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{cache_policy_passes, max_age_seconds, validate_url};

    #[test]
    fn requires_immutable_and_at_least_one_day() {
        assert!(cache_policy_passes(Some(
            "public, max-age=86400, immutable"
        )));
        assert!(!cache_policy_passes(Some("public, max-age=60, immutable")));
        assert!(!cache_policy_passes(Some("public, max-age=31536000")));
        assert!(!cache_policy_passes(None));
    }

    #[test]
    fn parses_s_maxage() {
        assert_eq!(
            max_age_seconds("public, s-maxage=31536000, immutable"),
            Some(31_536_000)
        );
    }

    #[test]
    fn rejects_non_http_and_userinfo_urls() {
        assert!(validate_url("file:///tmp/a.webp").is_err());
        assert!(validate_url("https://user:pass@example.com/a.webp").is_err());
        assert!(validate_url("https://example.com/a.webp").is_ok());
    }
}
