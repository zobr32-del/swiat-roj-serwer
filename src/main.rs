use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::env;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::Mutex;
use tokio::time::{self, Duration};

#[derive(Serialize, Deserialize, Debug, Clone)]
struct HarvestedItem {
    source: String,
    title: String,
    url: String,
    content: String,
    timestamp: DateTime<Utc>,
    is_verified: bool,
}

struct DataSourceHarvester {
    allowed_sources: HashSet<String>,
    client: reqwest::Client,
    // Bezpieczna, współbieżna pamięć podręczna na zebrane dane w pamięci serwera
    stored_items: Arc<Mutex<Vec<HarvestedItem>>>,
}

impl DataSourceHarvester {
    fn new() -> Self {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(15))
            .user_agent("DataHarvesterBot/1.0 (+https://github.com/zobr32-del/swiat-roj-serwer)")
            .build()
            .unwrap();

        let mut allowed_sources = HashSet::new();
        allowed_sources.insert("https://api.zweryfikowane-podcasty-techniczne.pl/feed".to_string());
        allowed_sources.insert("https://api.pewna-baza-wiedzy.org/v1/items".to_string());
        allowed_sources.insert("https://oficjalne-archiwum-naukowe.pl/rss".to_string());

        Self {
            allowed_sources,
            client,
            stored_items: Arc::new(Mutex::new(Vec::new())),
        }
    }

    fn validate_source(&self, url: &str) -> bool {
        self.allowed_sources.iter().any(|source| url.starts_with(source))
    }

    async fn fetch_from_source(&self, endpoint: &str) -> Result<Vec<HarvestedItem>, Box<dyn std::error::Error + Send + Sync>> {
        if !self.validate_source(endpoint) {
            eprintln!("[BEZPIECZEŃSTWO] Odrzucono niezweryfikowane źródło: {}", endpoint);
            return Ok(vec![]);
        }

        println!("[POBIERANIE] Pobieranie danych ze zweryfikowanego źródła: {}", endpoint);
        
        let response = self.client.get(endpoint).send().await?;
        
        if response.status().is_success() {
            let items: Vec<HarvestedItem> = response.json().await.unwrap_or_else(|_| vec![]);
            
            let verified_items = items.into_iter()
                .map(|mut item| {
                    item.is_verified = true;
                    item
                })
                .collect();

            Ok(verified_items)
        } else {
            eprintln!("[BŁĄD] Problem z dostępem do źródła: HTTP {}", response.status());
            Ok(vec![])
        }
    }

    async fn run_harvesting_loop(&self) {
        let interval_secs = env::var("HARVEST_INTERVAL_SECS")
            .unwrap_or_else(|_| "3600".to_string())
            .parse::<u64>()
            .unwrap_or(3600);

        let mut interval = time::interval(Duration::from_secs(interval_secs));

        loop {
            interval.tick().await;
            println!("\n[START CYKLU] Rozpoczęcie okresowego zbierania danych...");

            let sources_list: Vec<String> = self.allowed_sources.iter().cloned().collect();

            for source in sources_list {
                match self.fetch_from_source(&source).await {
                    Ok(items) => {
                        let mut cache = self.stored_items.lock().await;
                        for item in items {
                            println!("[SUKCES] Dodano do bufora rekord z: {} | Tytuł: {}", item.source, item.title);
                            cache.push(item);
                        }
                    }
                    Err(e) => eprintln!("[AWARIA] Błąd podczas pobierania ze źródła: {}", e),
                }
            }
            println!("[KONIEC CYKLU] Oczekiwanie na kolejną turę...");
        }
    }
}

#[tokio::main]
async fn main() {
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    println!("[START] Serwer Harvestera w Rust uruchomiony. Port: {}", port);

    let harvester = Arc::new(DataSourceHarvester::new());

    // Uruchomienie pętli zbierającej w tle
    let harvester_clone = Arc::clone(&harvester);
    tokio::spawn(async move {
        harvester_clone.run_harvesting_loop().await;
    });

    // Nasłuchiwacze HTTP dla Render
    let listener = TcpListener::bind(format!("0.0.0.0:{}", port)).await.unwrap();
    println!("[INFO] Serwer HTTP gotowy na zapytania JSON.");

    loop {
        let (mut socket, _) = match listener.accept().await {
            Ok(val) => val,
            Err(_) => continue,
        };

        let harvester_ref = Arc::clone(&harvester);
        tokio::spawn(async move {
            use tokio::io::{AsyncReadExt, AsyncWriteExt};

            let mut buf = [0; 1024];
            let _ = socket.read(&mut buf).await;

            // Pobranie aktualnej listy zweryfikowanych elementów z pamięci
            let cache = harvester_ref.stored_items.lock().await;
            let json_body = serde_json::to_string(&*cache).unwrap_or_else(|_| "[]".to_string());
            drop(cache);

            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                json_body.len(),
                json_body
            );

            let _ = socket.write_all(response.as_bytes()).await;
        });
    }
}
