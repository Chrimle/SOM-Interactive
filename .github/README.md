# SOM-Interactive
Interact with [SOM-institute](https://www.gu.se/som-institutet) Data!

> [!IMPORTANT]
> This project is not associated, endorsed or affiliated with the SOM-institute.
> 
> This project relies on publicized data by the SOM-institute. ❤️

> [!NOTE]
> This is a complement to [SOM-institute's Analysis Tool](https://som-institutet.se/dataanalys).

### Dev Notes
The Python script is converted to WebAssembly via shiny.
```bash
shinylive export . docs --template-dir template
```