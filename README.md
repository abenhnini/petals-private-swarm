This repository contains instructions on how to get a private Petals swarm running for experimentation.


## Notes
**Running Llama?** [Request access](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct) to its weights, then run `huggingface-cli login` in the terminal before loading the model.

**Privacy:** In a public swarm, your data will be processed with the help of other people. Petals does not provide privacy guarantees honest-but-curious peers. Learn more about privacy [here](https://github.com/bigscience-workshop/petals/wiki/Security,-privacy,-and-AI-safety).

## Running a private swarm
**Docker:** Run Petals' official Docker image for NVIDIA GPUs (or follow [this](https://github.com/bigscience-workshop/petals/wiki/Running-on-AMD-GPU) for AMD):

```bash
sudo docker run -p 31330:31330 --ipc host --gpus all --volume petals-cache:/cache --rm \
    learningathome/petals:main \
    python -m petals.cli.run_server --port 31330 meta-llama/Meta-Llama-3.1-405B-Instruct
```

## Resources
- [Petals paper](https://arxiv.org/pdf/2209.01188.pdf)
- [Petals FAQ](https://github.com/bigscience-workshop/petals/wiki/FAQ:-Frequently-asked-questions)

Wiki Guides:
- Launch a private swarm: [guide](https://github.com/bigscience-workshop/petals/wiki/Launch-your-own-swarm)
- Run a custom model: [guide](https://github.com/bigscience-workshop/petals/wiki/Run-a-custom-model-with-Petals)

Contributing:

Refer to the [FAQ](https://github.com/bigscience-workshop/petals/wiki/FAQ:-Frequently-asked-questions#contributing) on contributing.
