# Running in Swarm

1. Edit the `deploy.sh` script and put in your parameters
2. Use AWS CLI to log in to the region you want
3. Run `deploy.sh` or log into the AWS console and deploy the machines
   1. If recreating manually, make sure the Security Group allows for traffic between the nodes for docker swarm and allows SSH and 8089 (Locust Portal) into each node from your machine
4. Choose one of the machines to be the `manager`
5. SSH into the `manager` node
   1. Install docker
   2. Run `sudo docker swarm init --advertise-addr <local IP>`
   3. Make note of the swarm join command and token
   4. Create the registry with `sudo docker service create --name registry --publish 5000:5000 registry:2`
6. Log into each remaining node
   1. Install docker
   2. Run the `docker swarm join` command that was spit out earlier
7. Launch
   1. SSH into the `manager` node
   2. Edit the `docker-compose.yaml` as you see fit
   3. Copy `worker-variables.sample.env` into `worker-variables.env`
   4. Edit the `worker-variables.env` with the connection string, etc 
   5. Deploy the stack with `sudo docker stack deploy --compose-file ./docker-compose.yml locust`

## Troubleshooting
* Check port communication in the SG for the VPC you are using that allows docker nodes to communicate
* Check you can get to port `8089` via the SG
* Check (from the `manager`) the containers that were deployed where with `sudo docker node ps $(sudo docker node ls -q)`
* Did you edit the variables and compose files?

## Perf Tuning
* Your locust master may be working too hard. add: `deploy.resources.reservations.cpus: '48'` and `deploy.resources.reservations.memory: 8192M` or something
* Make your `users` simulated and `workers` exact multiples:
  * 19 Docker Swarm nodes? Try 190 locust workers (10x) and 38,000 users (200x)
* If your latency seems too high, maybe you have too many users. Users may "wait" until a CPU thread it open to do work, and thus latency is high. Reducing workers may retain same QPS and lower latency