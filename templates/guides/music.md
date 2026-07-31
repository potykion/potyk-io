# Музыка: Качаем, Размечаем

## Скачивание

### [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

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

## Разметка

- Скаченная музыка с например ютуба обычно без мета-данных, то есть просто мп3 без исполнителя, альбома, обложки и тд
- Чтоб выставить мета-данные (теги), юзаем спец
  проги: [Mp3Tag](https://www.mp3tag.de/en/), [MusicBee](https://getmusicbee.com)