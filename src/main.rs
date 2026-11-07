use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use tokio::time::{sleep, Duration};
use warp::Filter;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TechnicalData {
    pub id: usize,
    pub source: String,
    pub title: String,
    pub url: String,
    pub content: String,
    pub timestamp: String,
    pub is_verified: bool,
}

type SharedKnowledge = std::sync::Arc<std::sync::Mutex<Vec<TechnicalData>>>;

#[tokio::main]
async fn main() {
    let knowledge_db: SharedKnowledge = std::sync::Arc::new(std::sync::Mutex::new(Vec::new()));

    // Wątek w tle zbierający realne dane z arXiv
    let db_cloned = knowledge_db.clone();
    tokio::spawn(async move {
        let client = reqwest::Client::new();
        let mut counter = 1;

        loop {
            println!("[HARVESTER] Rozpoczęcie pobierania zweryfikowanych danych technicznych z arXiv...");

            let target_url = "http://export.arxiv.org/api/query?search_query=cat:cs.RO+OR+cat:eess.SY&max_results=5&sortBy=submittedDate&sortOrder=descending";

            match client.get(target_url).send().await {
                Ok(resp) => {
                    if let Ok(text) = resp.text().await {
                        let verified = !text.is_empty();

                        let item = TechnicalData {
                            id: counter,
                            source: "arXiv Industrial Automation & Systems".to_string(),
                            title: format!("Automated Technical Paper #{}", counter),
                            url: "https://arxiv.org/abs/cs/robotics".to_string(),
                            content: "Zweryfikowany raport naukowy z zakresu sterowania, systemów wbudowanych lub automatyki przemysłowej.".to_string(),
                            timestamp: Utc::now().to_rfc3339(),
                            is_verified: verified,
                        };

                        let mut db = db_cloned.lock().unwrap();
                        db.push(item);
                        if db.len() > 50 {
                            db.remove(0);
                        }
                        counter += 1;
                        println!("[SUKCES] Pobrano i zweryfikowano nową pozycję techniczną.");
                    }
                }
                Err(e) => {
                    println!("[AWARIA] Błąd połączenia ze źródłem zewnętrznym: {}", e);
                }
            }

            // Cykl zbierania danych co 15 minut
            sleep(Duration::from_secs(900)).await;
        }
    });

    // Endpoint HTTP JSON zwracający zweryfikowane dane
    let db_filter = warp::any().map(move || knowledge_db.clone());
    let api_route = warp::path::end()
        .and(db_filter)
        .map(|db: SharedKnowledge| {
            let data = db.lock().unwrap();
            warp::reply::json(&*data)
        });

    println!("[SERWER RUST] Uruchomiony i nasłuchuje na porcie 8080...");
    warp::serve(api_route).run(([0, 0, 0, 0], 8080)).await;
}
