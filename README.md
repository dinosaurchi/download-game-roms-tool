## Run the script

```shell
$ make download.all
```

All the downloaded file hash will be mapped in `./status.txt`

## Account info structure

For `archive.org` account info

```json
{
    "username": "",
    "password": ""
}
```

## Input CSV database structure

```
is_downloaded,title,platform,unit,size_gb,tags,link
No,3D Sonic The Hedgehog 2,3DS,1,0.0359,,https://archive.org/download/nintendo-3ds-eshop-complete-collection/z117%20-%203D%20Sonic%20The%20Hedgehog%202%20%28USA%29%20%28eShop%29.3ds.7z
No,Ace Combat - Joint Assault,PSP,1,1.3,,https://archive.org/download/redump.psp/Ace%20Combat%20-%20Joint%20Assault%20%28USA%29.zip
```