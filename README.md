<img align="left" width="80" src="https://raw.githubusercontent.com/devmel/hass_airsend/master/icons/icon.png" alt="App icon">

# AirSend for Home Assistant

Component for sending radio commands through the AirSend (RF433) or AirSend duo (RF433 & RF868).

## Installation Steps

1. **Add Repository**:
   - [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdevmel%2Fhass_airsend-addon)
   - Click on "Add repository" to include the necessary repository for the addon installation or follow [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon)

2. **Place the `airsend.yaml` File**:
   - Go to `airsend.cloud -> import/export -> Export`
   - Select your devices, for local connection, select `spurl`
   - Click `Export YAML` to save the airsend.yaml
   - In the `config` folder of Home Assistant, place the `airsend.yaml` file.

3. **Edit the `secrets.yaml` File**:
   - Add a line to the `secrets.yaml` file with the AirSend - Local IP - / - Password - (and IPv4 address).
   - If you know the IPv4 address, the line should look like this:
     ```yaml
     spurl: sp://**************@[fe80::xxxx:xxxx:xxxx:xxxx]?gw=0&rhost=192.168.xxx.xxx
     ```
   - or this if you don't know the IPv4 address :
     ```yaml
     spurl: sp://**************@[fe80::xxxx:xxxx:xxxx:xxxx]?gw=1
     ```
   - Replace `**************` with the AirSend Password, `fe80::xxxx:xxxx:xxxx:xxxx` with AirSend Local IP and `192.168.xxx.xxx` with the AirSend IPv4 address.

4. **Edit the `configuration.yaml` File**:
   - Add the following line to the `configuration.yaml` file to include the `airsend.yaml` file:
     ```yaml
     airsend: !include airsend.yaml
     ```

5. **Install the Custom Component**:
   - In the Home Assistant terminal, run the following command to install the component:
     ```bash
     wget -q -O - https://raw.githubusercontent.com/devmel/hass_airsend/master/install | bash -
     ```

6. **Restart Home Assistant and the AirSend Addon**:
   - Restart Home Assistant.
   - Restart the AirSend addon.

These steps will integrate AirSend with Home Assistant, allowing you to manage and automate AirSend-related tasks through the Home Assistant interface.


## Information 

   - This requires the execution of [hass_airsend-addon](https://github.com/devmel/hass_airsend-addon), if it is not on the same machine it is possible to add the field `internal_url: http://x.x.x.x:33863/` in airsend.conf
   - For local connection, the AirSend IPv4 address is required, you can find it in your router or [Airsend App for Windows](https://apps.microsoft.com/detail/9nblggh40m8w).

## Preview

<img src="https://raw.githubusercontent.com/devmel/hass_airsend/master/img/screenshot.png" height="200"/>
