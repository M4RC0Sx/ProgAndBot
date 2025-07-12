# ProgAndBot
Multi-purpose Discord bot for communities management.


## Features:
- **Multi-Guild**: Supports multiple servers with different configurations. Every server has its own settings.
- **Setting management**: Easily manage your server settings with commands like `/settings`. Everything is stored in database and can be configured using only bot commands. Everything is customizable.
- **Slash commands**: Use slash commands for a better user experience. All commands are slash commands.
- **Welcome system**: Automatically greet new members with a customizable message. Toogle it on or off.
- **Moderation**: Kick, ban, and manage members with ease. Use commands like `/kick`, `/ban`...
- **Chat cleaning**: Clean up your channels with commands like `/clear`.
- **Polls**: Create polls with multiple answers and emojis. Use `/poll` command.


## Installation

1. Clone the repository.
2. Install the Poetry environment:
   ```bash
   poetry install
   ```
3. Create a `.env` file with the variables you need to change from `progandbot/core/config.py`.
4. Run the bot:
   ```bash
   poetry run python -m progandbot
   ```
5. Invite the bot to your server using the OAuth2 URL generated in the Discord Developer Portal.
6. If you add or modify a slash command, you need to restart the bot and run the command `!sync`.

## Running as a Docker container
1. Build the Docker image:
   ```bash
   docker build -t progandbot .
   ```
2. Create a `.env` file with the variables you need to change from `progandbot/core/config.py`.
3. Run the Docker container:
   ```bash
   docker run -d --name progandbot --env-file .env progandbot
   ```

### Docker Compose
You can also use Docker Compose to run the bot. Create a `docker-compose.yml` file with the following content:

```yaml
services:
  progandbot:
    build: .
    env_file: .env
    restart: unless-stopped

  db:
    image: postgres
    restart: always
    shm_size: 128mb
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: progandbot
    ports:
      - "5432:5432"

  adminer:
    image: adminer
    restart: always
    ports:
      - "8081:8080"

```

Then run:
```bash
docker-compose up -d
```

## TODO List
- [x] Add configuration system for the bot.
- [x] Add configuration system for each server.
- [x] Add welcome system.
- [x] Add moderation basic commands.
- [x] Add polls system.
- [ ] Add system for roles management.
- [ ] Add system to notify when a streamer goes live on Twitch.
- [ ] Add system to notify when a YouTube channel uploads a new video.
- [x] Add user warnings system.
- [ ] Add user score system. With a printable leaderboard.
- [ ] Add system to allow users to convert between timezones.
- [ ] Add throw dice command.
- [ ] Add system to allow users to play rock-paper-scissors.
- [ ] Add throw coin command.
- [ ] Add system to make the bot join a voice channel and play a sound when a user boosts the server with Nitro.
- [x] Add user info command.
- [ ] Add user level/xp progress bar to the user info command output.
- [x] Make the bot able to send an image on the welcome message.
- [x] User message count tracking.
- [x] Multilanguage support, configurable by the server.
- [ ] Handle all messages with i18n translations.