FROM python:3.12-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Apache + CGI + RANCID + ViewVC + build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 \
      libapache2-mod-fcgid \
      rancid \
      viewvc \
      pkg-config \
      default-libmysqlclient-dev \
      gcc \
 && rm -rf /var/lib/apt/lists/*

# Enable CGI, FastCGI, and the ViewVC Apache config
RUN a2enmod cgi fcgid \
 && a2enconf viewvc

# Mirror original layout and set CWD
WORKDIR /usr/local/rancid
# If building in your /Users/mauro/rancid folder, this copies all your files into the container
COPY . .
# Create symlink so /usr/local/rancid/admin_rancid → /var/www/html/admin_rancid
RUN mkdir -p /var/www/html \
 && ln -s /usr/local/rancid/admin_rancid /var/www/html/admin_rancid \
 && chown -R www-data:www-data /usr/local/rancid


# Configure Apache to treat .py files as CGI
RUN sed -i '\|DocumentRoot /var/www/html| a\
\
<Directory /var/www/html> \
    Options +ExecCGI \
    AddHandler cgi-script .py \
</Directory>' \
    /etc/apache2/sites-available/000-default.conf

RUN pip install --no-cache-dir -r requirements.txt

# Expose HTTP port and launch Apache
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]


