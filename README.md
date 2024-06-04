# UDP communication for 2024 Cybathlon Game 🧠💻🎮

## Overview 
🪧
✨ Python class to send commands to the different games and receive information (device, start of a min-game). It also handles handcheck, heartbeat, etc in background.

Developed by [Ludovic DARMET](http://www.isc.cnrs.fr/index.rvt?language=en&member=ludovic%5Fdarmet) from the [DANC lab](https://www.danclab.com/) and [COPHY](https://www.crnl.fr/en/equipe/cophy), under the supervision of [Jimmy Bonaiuto](http://www.isc.cnrs.fr/index.rvt?member=james%5Fbonaiuto) and [Jérémie Mattout](https://www.crnl.fr/en/user/236).

## Contents
📁
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Example Usage](#example-usage)
- [Help](#help)

## Dependencies

- [Psychopy<sup>3</sup>](https://www.psychopy.org/download.html)
- [PyACQ](https://github.com/pyacq/pyacq/tree/master)
- [pylsl](https://github.com/chkothe/pylsl)
- [Sklearn](https://scikit-learn.org/stable/install.html)
- Pickle

## Installation
👩‍💻
Clone the repo:

```bash
git clone https://github.com/ludovicdmt/udp_cyb.git
cd ${INSTALL_PATH}
conda env create -f udp.yml
pip install -e .
```
This will install the module in editable mode. That means that any changes you do to the code will be updated so you don't have to re-install every time.

## Example Usage
🗜️
You could then use this class inside one of your Python script, see in `examples` folder.

## Help
🆘
If you encounter any issues while using this code, feel free to post a new issue on the [issues webpage](https://github.com/ludovicdmt/udp_cyb/issues). I'll get back to you promptly, as I'm keen on continuously improving it. 🚀

