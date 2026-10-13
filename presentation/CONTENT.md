# Scan and Pay 2.0 — presentation content

Source: `presentation/index.html`. Generated with `npm run content` in `presentation/`; edit the HTML source, then regenerate this companion.

25 slides. English slides and Croatian speaker notes; approximately 19–20 minutes including the live demo. Content retains the approved 9 October 2026 revision and its dated evidence. The repository edition uses a numbered corpus overview; original invoice previews are optional local assets.

## 1. Cover

### On slide

× Scan and Pay 2.0 An Azikus proof of concept for Aircash Ivan Markusi CEO, Azikus

### Speaker notes — Croatian

Scan and Pay već radi u Aircashu. Ovaj PoC pokazuje mogući sljedeći korak: čitanje ispisanih podataka s računa bez podržanog koda. Pokazat ću pristupe, rezultate i prototip. Ovo je tehnički dokaz koncepta, a ne produkcijski spremna funkcionalnost.

## 2. Scan and Pay in production

### On slide

Scan and Pay in production Live-frame code detection. Platform options: Android · ML Kit; iOS · native AVFoundation. 01 Open Scan and Pay 02 Automatic code detection 03 Unsupported code 04 Payment details Scan and Pay 2.0: extend the existing scanner to invoices without a supported code.

### Speaker notes — Croatian

Današnji Scan and Pay automatski obrađuje frameove iz kamere. Android prikazujemo s ML Kitom, a za iOS navodimo standardni Appleov nativni pristup: AVFoundation i AVCaptureMetadataOutput. To je pregled platformskih opcija, a ne potvrda unutarnje iOS implementacije Aircasha. ML Kit postoji i za iOS; nije isključivo Android alat. Korisnik ne mora fotografirati račun da bi skenirao podržani kod. Prikazujemo postojeći proces i iduću iteraciju za račune bez podržanog koda. Poruka na trećoj slici odnosi se na nepodržani testni barkod. Izvori: https://developers.google.com/ml-kit/vision/barcode-scanning ; https://developer.apple.com/documentation/avfoundation/avmetadatamachinereadablecodeobject . VisionKit DataScanner je Appleova viša razina za skeniranje teksta i kodova: https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera .

## 3. Aircash at scale

### On slide

Aircash at scale 15 + markets ALMOST 2M downloads More markets. More invoice formats. The next iteration can extend the existing frame-based scanner to documents without a supported payment code.

### Speaker notes — Croatian

Aircash posluje na više od 15 tržišta i ima gotovo dva milijuna preuzimanja, prema Markusovim podacima za ovaj razgovor. Naglasak je na raznolikosti jezika, izgleda računa i platnih podataka koju taj opseg donosi. Ne predstavljamo ovo kao prodajnu poruku Aircashu niti preuzimanja izjednačavamo s aktivnim korisnicima.

## 4. The Scan and Pay PoC

### On slide

The Scan and Pay PoC Invoice image in. Editable payment draft out. Read payment and invoice fields from the document. Review and correct the proposed values. Test extraction independently of the final capture interaction. DEMO INTERFACE Capture / import → crop → send → review → confirm

### Speaker notes — Croatian

Ovdje počinje pregled PoC-a, ne demonstracija uživo. Pokazujemo rezultat ekstrakcije i pregled korisnika. Današnji demonstracijski ekran koristi capture ili import, crop i Send, ali taj slijed nije ograničenje arhitekture. Buduća integracija može birati frameove iz postojećeg previewa i kombinirati put za kodove s ekstrakcijom slike. To još nije implementirano u ovom PoC-u. Demo uživo ostaje pred kraj.

## 5. How the components connect

### On slide

How the components connect Mobile app Image input Review and edit Image 101 Backend Job orchestration Result normalization 010 Extraction service 01 Image → direct LLM → fields 02 Image → OCR → rules → fields 03 Image → OCR → LLM → fields 1010 0101 1100 Results and run history Source image · fields · user edits Editable draft 1001 010 Admin Configure and inspect Three configurable extraction routes. A common structure for the mobile review.

### Speaker notes — Croatian

U trenutnom adminu biramo tri pristupa: direktnu sliku modelu, OCR s pravilima ili OCR nakon kojeg model interpretira tekst. Backend pokreće odabranu obradu i normalizira rezultat. Mobilna aplikacija prikazuje podatke za pregled, dok admin omogućuje pregled postupka i izbora. Dokumentni API-ji i OCR anotacije također su istraženi u širem skupu evaluacija, ali nisu dodatne aktivne opcije današnjeg pojednostavljenog admina. Animirani tok prikazuje smjer podataka, a ne broj zahtjeva ni stvarno trajanje obrade.

## 6. PoC Admin

### On slide

PoC Admin Choose the approach and model Inspect each run. Compare processing stages. Review the original result and edits. Image, result, provider output and mobile edits

### Speaker notes — Croatian

Admin pokazuje izbor metode i modela za sljedeći scan te daje pristup izvornom rezultatu, odgovoru servisa, poslanoj slici i korisničkim izmjenama. Prikazane su spremljene slike admina s ranijim izborom modela. Ne mijenjamo trenutačni izbor u aplikaciji.

## 7. Extraction approaches explored

### On slide

Extraction approaches explored Approach Input and interpretation Tested services Direct image model Image interpreted by a vision LLM OpenAI, Gemini, Mistral, Anthropic, Together, xAI OCR with rules Recognized text parsed by rules Mistral OCR, Google OCR, Azure Read, AWS Text Invoice extraction API Document-specific field extraction Azure Invoice, Google Invoice, AWS Expense, Mindee OCR with annotations OCR with a requested field schema Mistral annotations OCR followed by a model OCR text / layout interpreted by an LLM Mistral OCR + OpenAI Five approaches, tested through different service and model configurations.

### Speaker notes — Croatian

Provider family je u starijem tekstu označavao integraciju sa servisom, a ne nužno zasebnu tvrtku. Historical method je značio spremljenu testiranu konfiguraciju. Te nazive izbacujemo. Šira usporedba s tri prolaza obuhvatila je 15 konfiguracija: šest direktnih modela, četiri OCR servisa s pravilima, četiri invoice API-ja i Mistral anotacije. Hibrid OCR plus LLM testiran je zasebno kasnije.

## 8. Direct image models

### On slide

Direct image models APPROACH 01 Invoice image → Vision LLM → Structured fields How it works One model sees the document and returns the requested payment and invoice fields. What the PoC showed Fast results from a single external stage. Incorrect amounts, recipients and references still require review. OpenAI · Gemini · Mistral · Anthropic · Together · xAI

### Speaker notes — Croatian

Direktni model prima sliku i strukturirane upute. U jednom vanjskom pozivu pokušava očitati podatke i povezati ih s odgovarajućim ulogama. Prednost je jednostavniji tok i dobar rezultat u našoj usporedbi. I dalje smo vidjeli pogrešne iznose, primatelje i reference; strukturirani izlaz nije jamstvo točnosti.

## 9. OCR with rules

### On slide

OCR with rules APPROACH 02 Invoice image → OCR text / layout → Parsing rules → Structured fields How it works OCR recognizes the text. Deterministic rules locate identifiers and associate them with payment fields. What the PoC showed Text recognition can succeed while payment extraction stays incomplete. Layout and field relationships matter. Mistral OCR · Google Document AI OCR · Azure Read · AWS Textract Text

### Speaker notes — Croatian

OCR prepoznaje tekst, a zatim naša pravila određuju koja je vrijednost iznos, račun primatelja ili poziv na broj. Ispravna slova i znamenke nisu dovoljni bez dobrog povezivanja vrijednosti. U ranijoj strukturnoj evaluaciji mogući su bili odgovori bez korisnih platnih polja; zato broj vraćenih odgovora ne prikazujemo kao točnost.

## 10. Invoice extraction APIs

### On slide

Invoice extraction APIs APPROACH 03 Invoice image → Invoice API → Native fields → Payment mapping How it works A document service returns invoice-specific fields such as supplier, total, dates and line items. What the PoC showed Invoice fields do not always match payment intent. Supplier is not necessarily beneficiary; invoice total is not always amount due. Azure Invoice · Google Document AI Invoice · AWS Textract Expense · Mindee

### Speaker notes — Croatian

Ovi servisi već imaju shemu računa. Mi njihov rezultat prevodimo u polja potrebna za plaćanje. Tu nastaje važna razlika: dobavljač nije nužno primatelj uplate, a ukupni iznos računa nije nužno preostali iznos za uplatu. Testirali smo sve navedene servise; kasnija tablica sa šest modela odnosi se samo na direktne modele.

## 11. OCR with annotations

### On slide

OCR with annotations APPROACH 04 Invoice image → OCR + field schema → Structured annotations How it works The OCR request includes the structure we want back. The service returns text and schema-guided fields. What the PoC showed One integrated service call, with a separate cost and latency profile from basic OCR. Mistral OCR annotations

### Speaker notes — Croatian

Mistral anotacije kombiniraju OCR i traženu strukturu podataka u jednom servisnom zahtjevu. To nije ista cijena i isti način rada kao osnovni OCR. Trošak dodatka u sačuvanim evidencijama nije dovoljno provjeren za potpunu usporedbu, pa ga ne predstavljamo kao nulu ili kao potvrđenu cijenu osnovnog OCR-a.

## 12. OCR followed by a model

### On slide

OCR followed by a model APPROACH 05 Invoice image → OCR text / layout → LLM interpretation → Structured fields How it works OCR separates recognition from interpretation. The model then maps the recognized content to payment fields. What the PoC showed Both stages add latency and cost. In the tested configurations, this did not outperform direct image extraction. Mistral OCR + OpenAI

### Speaker notes — Croatian

Kod hibrida prvo vanjski OCR obradi sliku, a zatim model interpretira njegov tekst ili raspored. Mjerimo oba koraka. Ovaj pristup nije nadmašio direktnu sliku u testiranim konfiguracijama, ali to ne isključuje moguće poboljšanje na drugim dokumentima ili s drugačijim prikazom layouta.

## 13. Evaluation coverage

### On slide

Evaluation coverage 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 17 inputs · 13 with scored fields All 17 inputs used in the reviewed comparison BROAD SERVICE STUDY 15 configurations 31 images × 3 runs each 1,395 processing runs DIRECT-MODEL QUALITY STUDY 6 vision models 17 images per model 102 readable field checks 63 payment-field checks 98 separate absence checks Development sample. 13/17 images have scored fields; 146 fields remain excluded. Results describe fields, not whole-invoice success.

### Speaker notes — Croatian

Pregledana usporedba obuhvaća 17 ulaza. Postojeće maskiranje 2D kodova zadržano je u ulazima korištenima za test. Šira evaluacija već je obuhvatila sve implementirane servisne konfiguracije u tri prolaza. Šest modela u kasnijoj tablici predstavlja šest izravnih vision modela, a ne sav testirani rad. Dio oznaka još nije potvrđen i srodne stranice i duplikat ostaju u uzorku.

## 14. All tested configurations Direct models

### On slide

All tested configurations Direct models The broader processing study: three passes through 31 images Configuration Valid responses Errors Median time p95 time OpenAI GPT-4.1 mini 92 / 93 1 4.2 s 9.0 s Anthropic Haiku 4.5 91 / 93 2 5.7 s 10.1 s Gemini 3.5 Flash-Lite 93 / 93 0 3.1 s 5.0 s Mistral Small 87 / 93 6 3.4 s 6.2 s xAI Grok 4.7 92 / 93 1 25.5 s 50.4 s Together Qwen 3.5 9B 88 / 93 5 8.8 s 23.9 s Valid response = structurally processable output. This does not measure payment-field correctness. Backend times include failures.

### Speaker notes — Croatian

Ovo su svi direktni modeli iz šire ranije studije. Svaki ima 93 pokušaja: 31 slika u tri prolaza. Validan odgovor znači da je tada prošao strukturnu provjeru, ne da su podaci točni ili potpuni. Ova tablica govori o ponašanju integracija. Kasnija tablica kvalitete koristi drugačiji skup i novije konfiguracije, zato brojeve ne spajamo. Medijan je srednje vrijeme, p95 vrijeme unutar kojeg završava približno 95 posto pokušaja.

## 15. All tested configurations OCR and invoice APIs

### On slide

All tested configurations OCR and invoice APIs The same processing study, covering the remaining nine configurations Configuration Valid responses Errors Median time p95 time Mistral OCR + rules 93 / 93 0 3.0 s 6.5 s Google OCR + rules 93 / 93 0 2.1 s 2.7 s Azure Read + rules 93 / 93 0 6.0 s 11.2 s AWS Text + rules 93 / 93 0 2.5 s 4.4 s Azure Invoice 93 / 93 0 11.1 s 16.7 s Google Invoice 93 / 93 0 4.1 s 5.3 s AWS Expense 93 / 93 0 2.9 s 4.0 s Mindee Invoice 93 / 93 0 5.3 s 6.6 s Mistral annotations 91 / 93 2 11.3 s 29.7 s Structural validity does not establish correct or complete payment details. These services are included in the saved evidence.

### Speaker notes — Croatian

Ovdje su ostalih devet konfiguracija, također po 93 pokušaja. Pokazujemo da nismo testirali samo šest direktnih modela. Strukturna valjanost dokumentnih rezultata nije isto što i točnost platnih polja. Kasnija offline analiza otkrila je i rezultate bez mapiranih platnih polja, što je razlog da ne prikazujemo 93 od 93 kao poslovni uspjeh ili točnost.

## 16. Direct-image findings

### On slide

Direct-image findings Field-level correctness and backend processing time Model Readable fields /102 Payment fields /63 Median time p95 time OpenAI GPT-4.1 mini 79 51 4.02 s 9.43 s Gemini 3.5 Flash-Lite 80 50 3.31 s 5.00 s Together Qwen 3.5 9B 69 47 9.41 s 22.67 s Mistral Small 71 43 2.99 s 5.78 s Anthropic Haiku 4.5 65 42 5.64 s 11.14 s xAI Grok 4.7 16 10 90.06 s 90.13 s Payment fields Recipient, amount, currency, bank destination, payment model and reference. Median / p95 50% / 95% of measured processing times fall at or below these values. Field counts, not invoice success rates. Times include failures and exclude mobile capture, upload and rendering.

### Speaker notes — Croatian

U prethodnoj tablici critical je značilo platno kritična polja: primatelj, iznos, valuta, odredišni račun, model i poziv na broj. Sada ih nazivamo payment fields i definicija je na slajdu. Medijan je 50. percentil: pola izmjerenih vremena je do te vrijednosti. p95 je 95. percentil, mjera sporijeg kraja raspodjele. U malom uzorku od 17 nearest-rank p95 odgovara maksimumu; nije SLA ni obećanje buduće latencije. Ovo su vrijeme backend obrade i prihvaćena pojedinačna polja. Grokovi nedostupni odgovori ostaju u imenitelju i vremenu, pa nizak rezultat uključuje dostupnost, a ne samo pogrešno čitanje. Razlika od jednog prihvaćenog polja između OpenAI-a i Geminija nije dokaz statističke nadmoći.

## 17. Cost of direct-image models

### On slide

Cost of direct-image models Image-model costs estimated from saved input and output usage Model USD / image USD / 1,000 images Mistral Small $0.000795 $0.79 Together Qwen 3.5 9B $0.001075 $1.07 OpenAI GPT-4.1 mini $0.002278 $2.28 Gemini 3.5 Flash-Lite $0.002427 $2.43 Anthropic Haiku 4.5 $0.007673 $7.67 xAI Grok 4.7 Incomplete cost data Not comparable These are image-model inference costs for the tested sample. The 1,000-image column scales the same sample usage. It is a provider-cost estimate, not a full operating-cost forecast.

### Speaker notes — Croatian

Ova tablica uspoređuje samo direktne modele. Cijena se temelji na spremljenim ulaznim i izlaznim tokenima odnosno naplati koju je pružatelj vratio. Uklonjen je ukupan iznos za 17 slika jer je lakše usporediti cijenu po slici. Tisuću slika je linearna projekcija istog uzorka. Za Grok nepotpuna evidencija troška ne dopušta usporediv iznos. Cijene su iz spremljene evaluacije, ne nova komercijalna ponuda.

## 18. Cost of OCR and invoice APIs

### On slide

Cost of OCR and invoice APIs Document services use page, document or account-plan pricing Service Pricing unit USD per unit / cost status Mistral OCR Page $0.004 AWS Textract Text Page $0.0015 AWS Textract Expense Page $0.0100 Google Document AI OCR Page $0.0015 list rate Google Document AI Invoice Document, up to 10 pages $0.10 minimum Azure Read / Invoice F0 test tier Exact cost unverified Mindee Invoice Page 1 trial credit; cash cost unverified Mistral OCR annotations OCR + annotation processing Annotation surcharge unverified Different extraction routes, different billing units. OCR followed by an LLM incurs both stages. Rates reflect the saved evaluation basis.

### Speaker notes — Croatian

Da, prethodne dvije tablice jesu prikaz dviju skupina pristupa, ali nisu usporedba istih obračunskih jedinica. Direktni modeli naplaćuju modelsku potrošnju, a dokumentni servisi stranicu, dokument ili plan. Zato to sada jasno odvajamo. Googleov minimum po dokumentu posebno je važan. Ne zbrajamo ili rangiramo neprovjerene račune kao nultu cijenu. Za OCR plus LLM trebalo bi dodati oba troška. Recorded usage je uklonjen sa slajda, a izvorna evidencija ostaje sačuvana.

## 19. Direct image and OCR-assisted extraction

### On slide

Direct image and OCR-assisted extraction Configuration External stages Payment fields /63 Median time p95 time OpenAI direct image 1 51 4.02 s 9.43 s Mistral OCR + OpenAI · draft 1 2 44 6.58 s 11.14 s Mistral OCR + OpenAI · roles 3 2 37 6.02 s 8.47 s Direct image is the stronger starting point in these measurements. Same reviewed fields. Both hybrid stages are included; hybrid batches were run earlier.

### Speaker notes — Croatian

Provjerili smo i može li odvajanje OCR-a i interpretacije dati bolji rezultat. U ovim konfiguracijama nije donijelo više prihvaćenih kritičnih polja, a medijan obrade bio je viši. Oba koraka uključena su u mjerenje. Zato predlažem direktnu sliku kao početni smjer. To ne znači da hibridi nemaju smisla za druge dokumente ili kasnije poboljšanje. Ove konkretne hibridne serije rađene su ranije i uspoređene su istim pregledanim ključem.

## 20. PoC status and production requirements

### On slide

PoC status and production requirements WORKING NOW Mobile input and editable review Configurable extraction and operational inspection Traceable source results and user-confirmed values BEFORE PRODUCTION Independent invoices across target markets Quality and end-to-end latency targets Payment integration, platform coverage and reliability This is a proof of concept, not production ready. Incorrect amounts, recipients and references remain possible.

### Speaker notes — Croatian

Prototip radi od snimanja do pregleda i potvrde. Ipak, postoje pogrešno očitani iznosi, zamjene uloga primatelja i dobavljača te zamjene poziva na broj i broja računa. Validan format ili kontrolni zbroj ne dokazuju da je podatak točan. To su otvoreni tehnički zahtjevi za produkciju. Sljedeći korak uključuje neovisan skup računa iz ciljanih tržišta, mjerljive kriterije prihvata, vrijeme od korisničke radnje do spremnog pregleda, integraciju s Aircashovim uslugama i operativnu pouzdanost. Potrebna je i puna pokrivenost mobilnih platformi. Ne tražimo da današnji demo prihvatite kao gotovu produkcijsku funkcionalnost, nego da podržite smjer koji ćemo validirati i pripremiti za takvu upotrebu.

## 21. Current conclusion

### On slide

Current conclusion Direct-image extraction is the best starting point in the tested configurations. PROVISIONAL BASELINE OpenAI GPT-4.1 mini 51 / 63 payment fields 4.02 s backend median CLOSE, FASTER ALTERNATIVE Gemini 3.5 Flash-Lite 50 / 63 payment fields 3.31 s backend median Tested OCR → LLM routes were slower and recovered fewer payment fields. Provisional choice from this development sample. A one-field gap does not establish a clear model winner.

### Speaker notes — Croatian

Zaključak za sada je direktna obrada slike. U testiranim konfiguracijama daje bolji odnos očitanih platnih polja i vremena od OCR plus LLM hibrida. OpenAI GPT-4.1 mini zadržavamo kao početni evaluacijski kandidat: 51 od 63 platna polja i medijan 4,02 sekunde. Gemini ima 50 od 63 uz medijan 3,31 sekundu, pa je bliska i brža alternativa. Razlika od jednog polja nije statistički dokaz nadmoći. Šira OCR i document API studija mjerila je strukturnu valjanost, a ne istu potvrđenu kvalitetu platnih polja; ne tvrdimo da smo dokazali univerzalnu pobjedu nad svim dokumentnim API-jima. Preporuka ne mijenja trenutačni izbor modela u adminu. Za konačan izbor treba neovisan skup računa iz ciljnih tržišta i vrijeme od kamere do pregleda. Izvor: docs/PHASE2_CLOSEOUT.md i docs/M3_DIRECT_PROVIDER_RESULTS.md.

## 22. Future improvements

### On slide

Future improvements 01 Background frame processing Select stable preview frames and prepare a draft through backend OCR or a vision model. 02 ML detection + direct LLM Explore one scanning loop that combines ML code detection with direct image interpretation. Feasibility remains uncertain. 03 Adaptive processing Skip duplicates and blur, bound background calls and ignore outdated results. 04 Insufficient information Define required fields per payment type. Missing, unreadable or conflicting values → request a retake or manual completion. Research ideas for a future iteration. The combined ML/LLM approach is untested in this PoC.

### Speaker notes — Croatian

Prva ideja je odabir kvalitetnih stabilnih frameova i priprema podataka u pozadini. Druga je baš objediniti ML detekciju koda i direktnu LLM interpretaciju unutar jednog scanning procesa. Ne predstavljamo to kao gotovu kombinaciju dekodera i modela niti obećavamo da će raditi. Treba ispitati kada odabrati pojedini put, što kad oba nešto pronađu, koliki su latencija, dodatni pozivi i potrošnja baterije. Treća tema je kontrola broja zahtjeva i izbjegavanje odgovora sa stare slike. Četvrta je jasno definirati kada nema dovoljno podataka za pripremu potpunog nacrta: prema odabranom tipu plaćanja odrediti obvezna polja, primjerice iznos i valutu, odredišni račun te referencu kad je potrebna. Ako su obvezne vrijednosti nečitljive, nedostaju ili su međusobno proturječne, rezultat treba označiti nepotpunim, sačuvati korisna polja i jasno zatražiti novu snimku ili ručni unos. Bez ijednog korisnog polja vratiti nemogućnost obrade. Time ne dokazujemo točnost samouvjereno pogrešnih vrijednosti; pragovi i politika tek trebaju validaciju. Ne predlažemo proizvoljan prag LLM confidencea kao jamstvo. Svaki nacrt i dalje zahtijeva pregled korisnika.

## 23. Scan and Pay 2.0

### On slide

Scan and Pay 2.0 Keep the existing automatic code detection. Add extraction for invoices without a supported code. Validate models and capture strategies across target markets. PROPOSED NEXT STEP Validation with Aircash and integration planning.

### Speaker notes — Croatian

Predloženi smjer je iduća iteracija postojećeg Scan and Paya. Zadržavamo detekciju kodova i proširujemo pokrivenost čitanjem ispisanih podataka s računa. Direktni model je prema ovim rezultatima početni kandidat. Konačan model i način izbora frameova provjerili bismo na reprezentativnim računima iz početnih tržišta.

## 24. Live demonstration

### On slide

Live demonstration From a real document to a reviewable draft. DEMO INTERFACE Capture / import → crop → send → review → confirm Inspect the result, correct a field and confirm the review.

### Speaker notes — Croatian

Sada ću pokazati prototip na stvarnom dokumentu. Snimim ili uvezem sliku, uredim izrez i pritisnem Send. Do tog trenutka nema slanja slike na obradu. Rezultat se vraća kao strukturirani prijedlog podataka koji mogu usporediti sa slikom, ispraviti i dopuniti. Izvorni rezultat ostaje sačuvan, a moje izmjene spremaju se zasebno. Na kraju pregledam potvrdu. Ovaj Pay u prototipu potvrđuje i sprema pregled te vraća aplikaciju na početak. Ne izvršava stvarnu uplatu. Ako dokument nema podatke potrebne za plaćanje, ne očekujemo da ih sustav izmisli. Nepotpune i pogrešne rezultate također treba jasno prikazati. Nakon demonstracije prijeći na završni slajd. Na slici je sintetički primjer za vizualnu referencu. Markus upravlja aplikacijom. Agent ne šalje dokumente na obradu.

## 25. More to build together

### On slide

AIRCASH × AZIKUS More to build together Thank you for your trust and collaboration.

### Speaker notes — Croatian

Hvala na vremenu i povjerenju. Ovdje ostaviti prostor za razgovor o smjeru, početnim tržištima i vrstama računa. Završni kadar prati dedicated-team prezentaciju.
