This repository contains instructions on how to launch a private [Petals](https://github.com/bigscience-workshop/petals) swarm locally using Docker, including a [health monitoring app](https://github.com/petals-infra/health.petals.dev).

## Prerequisites
- **Docker** installed and running
- **Conda** installed
- A Hugging Face access token, if required by the model provider (e.g. Meta's Llama)

## Getting Started

* Clone this repository and run `launch_swarm.sh`:

* Recommended: run the script inside a `tmux` session to keep it active in the background:
```bash
tmux new -s petals
./launch_swarm.sh
```
This will launch the bootstrap node, worker nodes, and the health monitoring app.

* You can then generate text with your distributed LLM with the following steps:
  1. Find your bootstrap node ID inside `health.petals.dev/config.py`
  2. Edit `run_chatbot.py` to make it point to it
  3. Run `python run_chatbot.py`

## Script Workflow Overview
### 1. Bootstrap Node
* Starts the first Docker container (`petals-bootstrap`) with GPU 0

### 2. Extract Bootstrap Peer ID
* Script polls the bootstrap container logs until it finds the peer ID

### 3. Worker Nodes
* Launches three additional Docker containers (`petals-server-1` to `petals-server-3`) on GPUs 1–3
* Each worker joins the swarm using the bootstrap peer ID

### 4. Health Monitoring App

1. Clones `health.petals.dev` if not already present
2. Creates a Conda environment `petals` with Python 3.10
3. Installs dependencies
4. Updates `health.petals.dev/config.py` to use the bootstrap peer
5. Runs Flask app on port 5000

## Useful Commands

* View logs in real time:

```bash
docker logs -f <container_name>
```

* Stop all running containers:

```bash
docker stop $(docker ps -a -q)
```

* Remove stopped containers:

```bash
docker container prune
```

## Notes
* **Privacy:** In a public swarm, your data will be processed with the help of other people. Petals does not provide privacy guarantees with honest-but-curious peers. Learn more about privacy [here](https://github.com/bigscience-workshop/petals/wiki/Security,-privacy,-and-AI-safety).



### Resources

* [Petals paper](https://arxiv.org/pdf/2209.01188.pdf)
* [Petals FAQ](https://github.com/bigscience-workshop/petals/wiki/FAQ:-Frequently-asked-questions)

### Wiki Guides

* Launch a private swarm: [guide](https://github.com/bigscience-workshop/petals/wiki/Launch-your-own-swarm)
* Run a custom model: [guide](https://github.com/bigscience-workshop/petals/wiki/Run-a-custom-model-with-Petals)

### Contributing

Refer to the [FAQ](https://github.com/bigscience-workshop/petals/wiki/FAQ:-Frequently-asked-questions#contributing) for contribution guidelines.
