import setuptools
from pathlib import Path

setuptools.setup(
    name='k8s_env',
    version='0.0.1',
    description="A OpenAI Gym Env for kubernetes",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include="k8s_env*"),
    install_requires=['gym']  # 其他的依赖
)