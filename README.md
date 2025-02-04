**Building Open-Ended Embodied Agents with Internet-Scale Knowledge**

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Reference](#reference)
- [License](#license)

# Installation

The code is developed upon [Minedojo](https://github.com/MineDojo/MineDojo) , which requires Python ≥ 3.9. We have tested on Ubuntu 20.04. **Please follow [this guide](https://docs.minedojo.org/sections/getting_started/install.html#prerequisites)** to install the prerequisites first, such as JDK 8 for running Minecraft backend. We highly recommend creating a new [Conda virtual env](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) to isolate dependencies.

Then install the simulator, run:

```bash
git clone https://github.com/CraftJarvis/MC-Simulator && cd MC-Simulator
pip install -e .
```

You can run the script below to verify the installation. It takes a while to compile the Java code for the first time. After that you should see a Minecraft window pop up, with the same gaming interface that human players receive. You should see the message `[INFO] Installation Success` if everything goes well.

```bash
python minedojo/scripts/validate_install.py
```

Note that if you are on a headless machine, don't forget to prepend either `xvfb-run` or `MINEDOJO_HEADLESS=1`:

```bash
xvfb-run python minedojo/scripts/validate_install.py
# --- OR ---
MINEDOJO_HEADLESS=1 python minedojo/scripts/validate_install.py
```

# Getting Started

MineDojo provides a [Gym-style](https://www.gymlibrary.ml/) interface for developing embodied agents that interact with the simulator in a loop.  Here is a very simple code snippet of a hardcoded agent that runs forward and jumps every 10 steps in the "Harvest Wool" task:

```python
import minedojo

env = minedojo.make(
    task_id="harvest_wool_with_shears_and_sheep",
    image_size=(160, 256)
)
obs = env.reset()
for i in range(50):
    act = env.action_space.no_op()
    act[0] = 1    # forward/backward
    if i % 10 == 0:
        act[2] = 1    # jump
    obs, reward, done, info = env.step(act)
env.close()
```

Please refer to [this tutorial](https://docs.minedojo.org/sections/getting_started/sim.html) for a detailed walkthrough of your first agent. MineDojo features a multimodal observation space (RGB, compass, voxels, etc.) and a compound action space (movement, camera, attack, craft, etc.). See [this doc](http://docs.minedojo.org/sections/getting_started/sim.html#basic-observation-and-action-spaces) to learn more. We recommend you to reference the full [observation](http://docs.minedojo.org/sections/core_api/obs_space.html) and [action space](http://docs.minedojo.org/sections/core_api/action_space.html) specifications.

MineDojo can be extensively customized to be tailored to your research needs. Please check out customization guides on [tasks](https://docs.minedojo.org/sections/customization/task.html), [simulation](https://docs.minedojo.org/sections/customization/sim.html), and [privileged observation](https://docs.minedojo.org/sections/customization/privileged_obs.html).

# Reference

The simulator is developed upon [Minedojo](https://arxiv.org/abs/2206.08853). If you find the simulator useful, please consider citing minedojo.

```bibtex
@article{fan2022minedojo,
  title   = {MineDojo: Building Open-Ended Embodied Agents with Internet-Scale Knowledge},
  author  = {Linxi Fan and Guanzhi Wang and Yunfan Jiang and Ajay Mandlekar and Yuncong Yang and Haoyi Zhu and Andrew Tang and De-An Huang and Yuke Zhu and Anima Anandkumar},
  year    = {2022},
  journal = {arXiv preprint arXiv: Arxiv-2206.08853}
}
```

# License

| Component        | License                                                                                                                             |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Codebase (this repo)         | [MIT License](LICENSE)                                                                                                                      |
| YouTube Database | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/legalcode)                 |
| Wiki Database    | [Creative Commons Attribution Non Commercial Share Alike 3.0 Unported](https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode) |
| Reddit Database  | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/legalcode)                 |
