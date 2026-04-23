FROM python:3.10

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python packages
RUN pip install -r requirements.txt

# Run app
CMD ["python", "app.py"]