var sheetData = []
var sheetListDiv = document.getElementById("sheetList")

function getSheets() {
    const http = new XMLHttpRequest()
    
    http.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                sheetData = JSON.parse(this.responseText)
                updateSheetList()
            }
        }
    }
    
    http.open("GET", "/api/sheets", true)
    http.send()
}
setInterval(function() {getSheets()}, 10000)
getSheets()

const reverseStageLookup = ["Finals", "Semifinals", "Quarterfinals", "Eight-finals", "16th-finals", "32nd-finals", "64th-finals", "128th-finals", "256th-finals", "512th-finals", "1024th-finals"]
function updateSheetList() {
    sheetListDiv.innerHTML = ""
    var lastReverseStage = -1
    for (var i = 0; i < sheetData.length; i++ ) {
        if (sheetData[i].reverse_stage != lastReverseStage) {
            lastReverseStage = sheetData[i].reverse_stage
            var header = document.createElement("DIV")
            header.classList.add("stage-header")
            header.innerHTML = reverseStageLookup[lastReverseStage]
            sheetListDiv.appendChild(header)
        }
        
        var textSpan = document.createElement("SPAN")
        textSpan.innerHTML = "M" + sheetData[i].match + ", " + sheetData[i].team
        var printedSpan = document.createElement("SPAN")
        printedSpan.classList.add("printed-text")
        if (sheetData[i].printed) {
            printedSpan.innerHTML = " - printed"
        }
        sheetListDiv.appendChild(textSpan)
        sheetListDiv.appendChild(printedSpan)
        sheetListDiv.appendChild(document.createElement("BR"))
    }
}
