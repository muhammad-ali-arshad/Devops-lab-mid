# Midterm report screenshot checklist — FA23-BDS-024

1. GitHub repo page showing config.json, dataset/train.csv, Dockerfile, Jenkinsfile, tests.
2. GitHub Collaborator invitation to instructor.
3. Jenkins job `MIDTERM-FA23-BDS-024` Pipeline Script from SCM configuration.
4. GitHub Webhook settings + recent delivery HTTP status.
5. Jenkins Console Output showing checkout, retrain/test, Docker build, redeploy, metrics SHA.
6. `docker ps` showing only the newly deployed midterm container on 172.31.18.147:8000.
7. Public FastAPI `/metrics` response showing student ID, accuracy, training_rows, model_version, git_sha.
8. POST `/predict` result (curl/Postman).
9. Jenkins mail/sender configuration (do not show any credentials) and email arrival in instructor inbox if provided.
10. Proof that a second GitHub dataset commit triggered Jenkins automatically, with updated version/SHA.

Include repository URL and pipeline script in final report, as required by PDF.
