#!/bin/bash
set -e

MODEL="meta-llama/Llama-3.1-8B-Instruct"
NUM_BLOCKS=8 # Per docker container
AUTH_TOKEN="your_token_here"
PORT=31330


# Step 1: Bootstrap
docker run -d \
  --name petals-bootstrap \
  -p $PORT:$PORT \
  --gpus device=0 \
  --volume petals-cache:/cache \
  --volume ~/ppdi/petals:/home/petals \
  learningathome/petals:main \
  python -m petals.cli.run_server $MODEL \
    --new_swarm \
    --num_blocks $NUM_BLOCKS \
    --host_maddrs /ip4/0.0.0.0/tcp/$PORT \
    --token $AUTH_TOKEN


# Step 2: Extract bootstrap peer ID
BOOTSTRAP_PEER=""
echo "Waiting for bootstrap peer ID..."
while [ -z "$BOOTSTRAP_PEER" ]; do
    BOOTSTRAP_PEER=$(docker logs petals-bootstrap 2>&1 | grep -o "/ip4/[^']*" | grep -v "/ip4/127\.0\.0\.1" | head -n1)
    if [ -z "$BOOTSTRAP_PEER" ]; then
        sleep 1
    fi
done
echo "Bootstrap peer: $BOOTSTRAP_PEER"


# Step 3: Start workers on GPUs 1–3
for GPU in 1 2 3; do
  docker run -d \
    --name petals-server-$GPU \
    --gpus device=$GPU \
    --volume petals-cache:/cache \
    --volume ~/ppdi/petals:/home/petals \
    learningathome/petals:main \
    python -m petals.cli.run_server $MODEL \
      --initial_peers $BOOTSTRAP_PEER \
      --num_blocks $NUM_BLOCKS \
      --token $AUTH_TOKEN
done


# Step 4: Health app
if [ ! -d health.petals.dev ]; then
  git clone https://github.com/petals-infra/health.petals.dev
fi
cd health.petals.dev

# Step 4.1: Setup virtual environment (conda)
ENV_NAME="petals"
if ! conda env list | grep -q "^$ENV_NAME"; then
    conda create -y -n $ENV_NAME python=3.10
fi
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME
pip install -r requirements.txt
pip install "pydantic<2.0"

# Step 4.2: Update ./health.petals.dev/config.py
CONFIG_FILE="config.py"
sed -i "s|^INITIAL_PEERS = .*|INITIAL_PEERS = ['$BOOTSTRAP_PEER']|" "$CONFIG_FILE" # s|...|...| → substitute the first pattern with the second

# Step 4.3: Run the app
flask run --host=0.0.0.0 --port=5000
