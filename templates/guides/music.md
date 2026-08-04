---
cover: /static/img/covers/music-download.png
---

# Скачать музыку бесплатно и без смс

![music-download.png](/static/img/covers/music-download.png)

## YouTube

- Ютуб - одно из лучших музыкальных хранилищ в плане сохранности музыки
- Так тут можно послушать [Kunteynir без цензуры](https://www.youtube.com/watch?v=BE1tgUfr_oU&list=OLAK5uy_n3nVXdYYZJww1geD_d6dV23FZMiuT8fsM&index=2)

###  [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- CLI для скачивания youtube видиков с возможностью конвертации в аудио
- Качаем exe с github, запускаем команды на скачивание (очевидно под vpn)

#### Скачивание плейлиста

```shell
yt-dlp -x --audio-format mp3 --audio-quality 0 --yes-playlist https://www.youtube.com/playlist?list=...
```

- Пример ссылки: https://www.youtube.com/playlist?list=OLAK5uy_mmTEiaINZstCOBj8hFkcd9GDv3kP_g6Bs
- `-x` - конвертация в аудио
- `--audio-format mp3` - конвертация в mp3
- `--audio-quality 0` - лучшее качество; 9 - худшее
- `--yes-playlist` - явно указывает что передается плейлист

### А есть нормальный интерфейс?

- https://ytdlp.online

## Яндекс Музыка

- https://github.com/Stmol/yandex-music-downloader
- https://github.com/llistochek/yandex-music-downloader
- https://github.com/MarshalX/yandex-music-api

## Разметка

- Скаченная музыка с того же ютуба обычно без мета-данных, то есть просто мп3 без исполнителя, альбома, обложки и тд
- Чтоб выставить мета-данные (теги), юзаем спец
  проги: [Mp3Tag](https://www.mp3tag.de/en/), [MusicBee](https://getmusicbee.com)