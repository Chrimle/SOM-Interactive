# SOM-Interactive
Interact with [SOM Institute](https://www.gu.se/som-institutet) Data!

> [!CAUTION]
> This project is not associated, endorsed or affiliated with the SOM Institute.
> 
> This project relies on publicized data by the SOM Institute.

> [!TIP]
> This is a complement to [SOM Institute's Analysis Tool](https://som-institutet.se/dataanalys).

### Dev Notes
The Python script is converted to WebAssembly via shiny.
```bash
cd src/
shinylive export . ../docs
```