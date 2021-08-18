# pandora-boxx

## Installation

1. Install asdf  
    ```bash
    brew install asdf 
    echo -e "\n. $(brew --prefix asdf)/libexec/asdf.sh" >> ${ZDOTDIR:-~}/.zshrc
    ```
    http://asdf-vm.com/guide/getting-started.html
2. Install asdf plugins
    ```bash
    asdf plugin add python
    asdf plugin add postgres
    asdf plugin-add golang https://github.com/kennyp/asdf-golang.git
    asdf install
    ```
3. Install goose for db migrations
    ```bash
    go get -u github.com/pressly/goose/v3/cmd/goose
    asdf reshim
   ```
   
 ## Usage
1. Start the postgres db
    ```bash
    pg_ctl -D ./db/data start
    ```
2. Provision the postgres db by applying migrations
    ```bash
    goose postgres 'dbname=pandora_boxx host=127.0.0.1 sslmode=disable' up
    ```
3. Start the web server
    ```bash
    pip install pipenv
    asdf reshim
    pipenv install
    pipenv run python -m aiohttp.web -H localhost -P 8080 pandora_boxx.__main__:main
    ```
4. Stop the postgres db when done
    ```bash
    pg_ctl -D ./db/data stop
    ```