# CSC418 DevOps Lab Midterm — FA23-BDS-024

Ready-to-use starter code plus CI/CD files derived from the supplied midterm PDF.

**GitHub**: https://github.com/muhammad-ali-arshad/Devops-lab-mid  
**EC2**: 54.235.141.196 (private IP: 172.31.18.147)  
**Jenkins job**: `MIDTERM-FA23-BDS-024`  
**Image**: `ali024024/devops-lab-mid`  
**Service**: http://54.235.141.196:8000/metrics

## What is included

- `config.json` — student's provided `FA23-BDS-024.json` renamed as required.
- `dataset/train.csv` — generated 300-row initial dataset (checked in to Git).
- Original instructor `app.py`, `train.py`, `generate_dataset.py`, `requirements.txt`.
- `Dockerfile` — installs dependencies, retrains, runs unit/API tests, and starts FastAPI.
- `Jenkinsfile` — GitHub checkout, train/test/build, redeploy to EC2, health checks, and email.
- `tests/test_midterm.py` — validates data, hash-based version, git SHA, health/metrics, prediction.

## Windows: push the project to your existing GitHub repository

1. In PowerShell:

   ```powershell
   cd 'C:\7th semester\DEV-OPS\lab-mid'
   git clone https://github.com/muhammad-ali-arshad/Devops-lab-mid.git
   ```

2. Extract the contents of the provided ZIP **into** `C:\7th semester\DEV-OPS\lab-mid\Devops-lab-mid`, preserving its `.git` folder. You can use Windows Explorer or:

   ```powershell
   Expand-Archive -LiteralPath 'C:\Path\To\DevOps_Midterm_FA23-BDS-024_Ready.zip' -DestinationPath 'C:\7th semester\DEV-OPS\lab-mid\Devops-lab-mid' -Force
   ```

3. Then:

   ```powershell
   cd 'C:\7th semester\DEV-OPS\lab-mid\Devops-lab-mid'
   git add .
   git commit -m 'Implement FA23-BDS-024 automatic ML retraining pipeline'
   git push origin main
   ```

## EC2: prerequisites / non-destructive checks

```bash
free -h
df -h /
sudo -u jenkins docker ps
sudo ss -ltnp 'sport = :8000'
ip -4 addr show dev ens5
```

If `jenkins` cannot access Docker, a suitable agent/permissions arrangement is needed.
**Note:** adding the Jenkins account to the Docker group grants root-equivalent host
privileges to Jenkins pipelines. Only consider this for your dedicated lab machine, with
appropriately restricted Jenkins and repository access. No existing containers should be
stopped to fix this.

## Jenkins job setup

1. Create new item `MIDTERM-FA23-BDS-024` of type **Pipeline**.
2. Set **Definition** to `Pipeline script from SCM`, SCM `Git`.
3. URL: `https://github.com/muhammad-ali-arshad/Devops-lab-mid.git`.
4. Branch: `*/main`, script path: `Jenkinsfile`.
5. Enable `GitHub hook trigger for GITScm polling` (if shown). `triggers { githubPush() }` is also in the Jenkinsfile.
6. For the SMTP notification, change the `SENDER_EMAIL` variable in Jenkinsfile
   to the actual sender account and configure **Manage Jenkins > System > E-mail Notification**
   for that account. Never commit SMTP passwords to GitHub.
7. Optional Docker Hub pushing: set job parameter `PUSH_DOCKERHUB=true` and
   create Jenkins Credentials of type Username with password, ID `dockerhub-ali024024`,
   Docker Hub username `ali024024`, password = Docker Hub personal access token.
   Push is *not* required by the examiner's stated rubric; leave disabled until core pipeline works.

## GitHub webhook

- Repo > Settings > Webhooks > Add webhook.
- Payload URL: `http://54.235.141.196:8081/github-webhook/`
- Content type: `application/json`; event: `Just the push event`; Active: yes.
- This requires GitHub's servers to reach the Jenkins endpoint; protect your Jenkins controller
  (ideally HTTPS with allowed GitHub webhook source IPs, and separately your own access),
  and check **Recent Deliveries** for HTTP 200 and Jenkins build history.
- GitHub's webhook should **not** be confused with `/github-webhook` (missing final slash).

## Instructor access, HTTP test, and submission

- Repo > Settings > Collaborators > Add `qasimalik@gmail.com` (GitHub may resolve invitation via its username).
- Grant inbound TCP 8000 to the necessary graders in EC2 Security Group; no reason to expose
  the entire EC2 unrestricted otherwise. Confirm EC2 `/metrics` is externally reachable.
- Test: `curl http://54.235.141.196:8000/metrics`
- POST test: `curl -X POST http://54.235.141.196:8000/predict -H 'Content-Type: application/json' -d '{"records":[{"voltage_drift":0.1,"thermal_load":0.2,"supply_variance":0.1,"demand_spike":0.3}]}'`
- Submit four fields: ID; GitHub repo URL; http://54.235.141.196:8000/metrics; actual sender email.
- Google Form: https://forms.gle/VSa1MDnAHvUoTk9B7
- Add a report with screenshots and Jenkinsfile, per the PDF.

## How training and versioning work

The `Dockerfile` executes `train.py` and the unit tests during each image build. The
Docker cache invalidates training when the dataset or Git revision changes; the `BUILD_COMMIT`
build argument is recorded as `git_sha`. The resulting model and metrics are included in
the image and served from `/metrics` and `/predict`.

## Existing port 8000 caveat

The host already has Gunicorn on **127.0.0.1:8000**. Our Docker run deliberately publishes
on **172.31.18.147:8000**, leaving loopback unchanged. This is supported by Docker on
Linux with IP-specific port publishing. Verify the private IP is still attached to EC2
and that no listener occupies that specific IP/port. If this fails, do not stop Gunicorn;
diagnose the bind conflict first.

## Resources

The EC2 was reported as having only 908.6 MiB RAM. Image builds can pressure the
system. Check `free -h` / `docker stats` and do not shut down any other services.
