---
status: new
---

Из page.html вынеси 

 main {
        margin: auto;
        max-width: 600px;
    }
    h4 {
        margin: 0;
    }
    ul {
        padding: 0 20px ;
    }
    blockquote {
        border-left: 5px solid #e8e8e8;
        padding-left: 10px;
        margin-left: 0;
    }
    img {
        width: 100%;
    }
 
в отдельный файл 

добавь на main какой-нибудь класс, типа md-content 

И при рендеринге заметок в ленте тоже используй этот класс и подключи css

Суть в том чтобы при просмотре мд и в ленте мд стили были едиными, а то сейчас в ленте картинки выезжают из карточки, а с видз=100 не выезжали бы