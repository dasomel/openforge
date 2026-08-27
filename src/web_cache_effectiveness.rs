use crate::Finding;
use reqwest::{
    blocking::Client,
    header::{AGE, HeaderMap},
    redirect::Policy,
};
use std::time::Duration;

const WEIGHT: f64 = 6.0;

#[derive(Debug, Default, PartialEq, Eq)]
struct CacheSignal {
    age: Option<u64>,
    cache_status: Option<String>,
    cf_cache_status: Option<String>,
    x_cache: Option<String>,
    x_cache_hits: Option<u64>,
}

fn header_text(headers: &HeaderMap, name: &str) -> Option<String> {
    headers
        .get(name)
        .and_then(|value| value.to_str().ok())
        .map(str::to_string)
}

fn signal(headers: &HeaderMap) -> CacheSignal {
    CacheSignal {
        age: headers
            .get(AGE)
            .and_then(|value| value.to_str().ok())
            .and_then(|value| value.parse().ok()),
        cache_status: header_text(headers, "cache-status"),
        cf_cache_status: header_text(headers, "cf-cache-status"),
        x_cache: header_text(headers, "x-cache"),
        x_cache_hits: header_text(headers, "x-cache-hits").and_then(|value| value.parse().ok()),
    }
}

fn text_indicates_hit(value: &str) -> bool {
    let value = value.to_ascii_lowercase();
    value.contains("hit") && !value.contains("miss")
}

fn indicates_hit(signal: &CacheSignal) -> bool {
    signal.age.is_some_and(|age| age > 0)
        || signal.x_cache_hits.is_some_and(|hits| hits > 0)
        || signal
            .cache_status
            .as_deref()
            .is_some_and(text_indicates_hit)
        || signal
            .cf_cache_status
            .as_deref()
            .is_some_and(text_indicates_hit)
        || signal.x_cache.as_deref().is_some_and(text_indicates_hit)
}

fn validate_url(url: &str) -> Result<(), &'static str> {
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return Err("cache effectiveness URL must use http:// or https://");
    }
    if url.contains('@') {
        return Err("cache effectiveness URL must not contain userinfo credentials");
    }
    Ok(())
}

fn client() -> Result<Client, ()> {
    Client::builder()
        .connect_timeout(Duration::from_secs(5))
        .timeout(Duration::from_secs(10))
        .redirect(Policy::none())
        .build()
        .map_err(|_| ())
}

fn probe(client: &Client, url: &str) -> Result<CacheSignal, String> {
    let response = client
        .head(url)
        .send()
        .map_err(|_| "head_request_failed".to_string())?;
    if !response.status().is_success() {
        return Err(format!("http_status={}", response.status().as_u16()));
    }
    Ok(signal(response.headers()))
}

fn evidence(prefix: &str, signal: &CacheSignal) -> Vec<String> {
    let mut evidence = Vec::new();
    if let Some(age) = signal.age {
        evidence.push(format!("{prefix}_age={age}"));
    }
    if let Some(value) = &signal.cache_status {
        evidence.push(format!("{prefix}_cache-status={value}"));
    }
    if let Some(value) = &signal.cf_cache_status {
        evidence.push(format!("{prefix}_cf-cache-status={value}"));
    }
    if let Some(value) = &signal.x_cache {
        evidence.push(format!("{prefix}_x-cache={value}"));
    }
    if let Some(hits) = signal.x_cache_hits {
        evidence.push(format!("{prefix}_x-cache-hits={hits}"));
    }
    evidence
}

pub(crate) fn finding(url: Option<&str>) -> Finding {
    let Some(url) = url else {
        return Finding {
            rule_id: "WEB-009".to_string(),
            category: "Web Assets".to_string(),
            title: "Runtime cache effectiveness is observable".to_string(),
            status: "SKIP",
            score: 0.0,
            weight: 0.0,
            evidence: vec!["no explicit --web-cache-effectiveness-url provided".to_string()],
            remediation: String::new(),
        };
    };

    if let Err(reason) = validate_url(url) {
        return failed(vec![format!("probe_error={reason}")]);
    }

    let client = match client() {
        Ok(client) => client,
        Err(()) => {
            return failed(vec![
                "probe_error=http_client_initialization_failed".to_string(),
            ]);
        }
    };

    let first = match probe(&client, url) {
        Ok(signal) => signal,
        Err(reason) => return failed(vec![format!("first_probe_error={reason}")]),
    };
    let second = match probe(&client, url) {
        Ok(signal) => signal,
        Err(reason) => return failed(vec![format!("second_probe_error={reason}")]),
    };

    let passed = indicates_hit(&second)
        || second
            .age
            .zip(first.age)
            .is_some_and(|(second_age, first_age)| second_age >= first_age && second_age > 0);

    let mut observed = evidence("first", &first);
    observed.extend(evidence("second", &second));
    if observed.is_empty() {
        observed.push("cache_signal_headers=none".to_string());
    }

    Finding {
        rule_id: "WEB-009".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime cache effectiveness is observable".to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { WEIGHT } else { 0.0 },
        weight: WEIGHT,
        evidence: observed,
        remediation: "Expose observable cache-hit evidence such as Age, Cache-Status, CF-Cache-Status, X-Cache, or X-Cache-Hits for the explicit endpoint.".to_string(),
    }
}

fn failed(evidence: Vec<String>) -> Finding {
    Finding {
        rule_id: "WEB-009".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime cache effectiveness is observable".to_string(),
        status: "FAIL",
        score: 0.0,
        weight: WEIGHT,
        evidence,
        remediation: "Provide a reachable explicit HTTP(S) image URL and ensure repeated requests expose cache-hit evidence.".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{CacheSignal, indicates_hit, text_indicates_hit};

    #[test]
    fn recognizes_common_hit_headers() {
        assert!(text_indicates_hit("HIT"));
        assert!(text_indicates_hit("Cloudflare; hit"));
        assert!(!text_indicates_hit("MISS"));
        assert!(!text_indicates_hit("HIT; fwd=uri-miss"));
    }

    #[test]
    fn recognizes_age_and_hit_count() {
        assert!(indicates_hit(&CacheSignal {
            age: Some(1),
            ..Default::default()
        }));
        assert!(indicates_hit(&CacheSignal {
            x_cache_hits: Some(2),
            ..Default::default()
        }));
        assert!(!indicates_hit(&CacheSignal::default()));
    }
}
