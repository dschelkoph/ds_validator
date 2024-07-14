ARG UBUNTU_TAG
FROM ubuntu:${UBUNTU_TAG}

ARG PYTHON_VERSION \
    USER=dev \
    DEBIAN_FRONTEND=noninteractive \
    TZ_AREA=America \
    TZ_ZONE=New_York
ARG USER_HOME=/home/${USER}
ARG VIRTUAL_ENV_PATH=${USER_HOME}/.venv/project

ENV TZ=${TZ_AREA}/${TZ_ZONE} \
    PATH=${PATH}:${VIRTUAL_ENV_PATH}/bin:${USER_HOME}/.local/bin:/workspace/.devcontainer/scripts \
    PYTHONPATH=/workspace/python:${VIRTUAL_ENV_PATH} \
    PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=${VIRTUAL_ENV_PATH}

RUN --mount=type=cache,target=/var/cache/apt \
    <<EOF
# in ubuntu 24.04, an ubuntu user was added by default
# remove it to make room for the `USER` to be UID = 1000
userdel --remove ubuntu

DIST_CODENAME=$(cat /etc/lsb-release | awk -F= '/DISTRIB_CODENAME/ {print $2}')
apt-get update
apt-get install --no-install-recommends --yes curl gpg ca-certificates

DEADSNAKES_KEY=/usr/share/keyrings/deadsnakes.gpg
curl --fail --location --silent --show-error "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf23c5a6cf475977595c89f51ba6932366a755776" | gpg --dearmor --output ${DEADSNAKES_KEY}
echo "deb [signed-by=${DEADSNAKES_KEY}] http://ppa.launchpad.net/deadsnakes/ppa/ubuntu ${DIST_CODENAME} main" >> /etc/apt/sources.list
echo "deb-src [signed-by=${DEADSNAKES_KEY}] http://ppa.launchpad.net/deadsnakes/ppa/ubuntu ${DIST_CODENAME} main" >> /etc/apt/sources.list

update-ca-certificates

echo "tzdata tzdata/Areas select ${TZ_AREA}" | debconf-set-selections
echo "tzdata tzdata/Zones/${TZ_AREA} select ${TZ_ZONE}" | debconf-set-selections

apt-get update
apt-get install --no-install-recommends --yes \
  bash-completion \
  git \
  iputils-ping \
  less \
  nano \
  python${PYTHON_VERSION} \
  python${PYTHON_VERSION}-venv \
  sudo \
  vim

useradd --create-home --shell /bin/bash ${USER}
echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}
EOF

USER ${USER}

RUN --mount=type=cache,target=/var/cache/apt,uid=1000 \
    --mount=type=cache,target=/home/${USER}/.cache/pip,uid=1000 \
    --mount=type=cache,target=/home/${USER}/.cache/pipx,uid=1000 \
    <<EOF
sudo apt-get update
sudo apt-get install --no-install-recommends --yes pipx
curl --fail --location --silent --show-error https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} -
python${PYTHON_VERSION} -m pip install --user pipx
pipx install ruff
pipx install poetry
pipx install scalene

mkdir --parents ${USER_HOME}/.local/share/bash-completion/completions
poetry completions bash > ${USER_HOME}/.local/share/bash-completion/completions/poetry
mkdir --parents ${USER_HOME}/.cache/pypoetry
python${PYTHON_VERSION} -m venv ${USER_HOME}/.venv/project
EOF

CMD ["sleep", "infinity"]