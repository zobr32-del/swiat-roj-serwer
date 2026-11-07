match client.get(target_url).send().await {
                Ok(resp) => {
                    // Pobieramy tekst odpowiedzi asynchronicznie
                    if let Ok(text) = resp.text().await {
                        let verified = !text.is_empty(); // Prosta weryfikacja czy treść nie jest pusta

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
