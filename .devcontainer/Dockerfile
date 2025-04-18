# Use the official Python image from Microsoft
FROM mcr.microsoft.com/devcontainers/python:3.12

# Set the working directory
WORKDIR /workspace

# Copy requirements.txt into the container
COPY  .  .



# Ensure zsh.zshrc exists in the build context or adjust the path
COPY .devcontainer/zsh.zshrc  .

# Ensure it's sourced from /etc/zsh/zshrc
RUN echo '[ -f ~/.zsh.zshrc ] && . ~/.zsh.zshrc' >> /etc/zsh/zshrc


# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip3 install --no-cache-dir -r requirements.txt; fi


# Install Google Cloud CLI
RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-cli
