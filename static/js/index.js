var canvas = document.getElementById("mainCanvas")
var context = canvas.getContext("2d")
var matchData = []
var scaler = 0.55

function updateResolution() {
    canvas.height = window.innerHeight * 0.98 * 2
    canvas.width = window.innerWidth * 0.98 * 2
    render()
}
updateResolution()
window.addEventListener("resize", function() {updateResolution()})

function getMatchData() {
    const http = new XMLHttpRequest()
    
    http.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                result = JSON.parse(this.responseText)
                matchData = result.matches
                document.getElementById("eventName").innerHTML = result.event
                window.document.title = result.event + " Playoffs"
                render()
            }
        }
    }
    
    http.open("GET", "/api", true)
    http.send()
}
setInterval(function() {getMatchData()}, 10000)
getMatchData()

function x(pos) {
    return (pos * scaler) + (canvas.width / 2)
}

function y(pos) {
    return (pos * scaler) + (canvas.height / 2)
}

function dis(dis) {
    return dis * scaler
}

function drawMatch(match, xPos, yPos) {
    // draw winner background
    context.fillStyle = "#00FF00"
    if (match.winner == 1) {
        context.fillRect(x(xPos-200), y(yPos-100), dis(400), dis(100))
    } else if (match.winner == 2) {
        context.fillRect(x(xPos-200), y(yPos), dis(400), dis(100))
    }
    
    // draw outline
    context.lineWidth = dis(7)
    context.lineCap = "butt"
    context.strokeStyle = "#000000"
    context.strokeRect(x(xPos-200), y(yPos-100), dis(400), dis(200))
    context.beginPath()
    context.moveTo(x(xPos-200), y(yPos))
    context.lineTo(x(xPos+200), y(yPos))
    context.stroke()
    
    // time
    context.textAlign = "center"
    context.textBaseline = "bottom"
    context.font = dis(80).toString() + "px sans-serif"
    context.fillStyle = "#000000"
    context.fillText(match.time, x(xPos), y(yPos-110))
    
    // teams
    context.textAlign = "center"
    context.textBaseline = "middle"
    context.font = dis(53).toString() + "px sans-serif"
    context.fillStyle = "#000000"
    context.fillText(match.team1, x(xPos), y(yPos-50))
    context.fillText(match.team2, x(xPos), y(yPos+50))
}

function render() {
    context.clearRect(0, 0, 3000, 1600)
    columnData = {}
    for (var i = 0; i < matchData.length; i++ ) {
        match = matchData[i]
        if (!(match.column in columnData)) {
            columnData[match.column] = {"min": match.match, "max": match.match}
        } else {
            if (match.match < columnData[match.column].min) {
                columnData[match.column].min = match.match
            }
            if (match.match > columnData[match.column].max) {
                columnData[match.column].max = match.match
            }
        }
    }
    
    columns = Object.keys(columnData).map(Number)
    maxColumn = 0
    for (var i = 0; i < columns.length; i++ ) {
        if (Math.abs(columns[i]) > maxColumn) {
            maxColumn = Math.abs(columns[i])
        }
    }
    scaler = canvas.width / 2 / ((maxColumn * 600) + 230)
    
    matchPositions = {}
    for (var i = 0; i < matchData.length; i++ ) {
        match = matchData[i]
        columnPos = match.match - columnData[match.column].min + 1
        margin = (canvas.height / scaler) / ((columnData[match.column].max - columnData[match.column].min) + 2)
        matchPositions[match.match] = [match.column * 600, ((0 - (canvas.height / 2)) / scaler) + (columnPos * margin)]
        drawMatch(match, matchPositions[match.match][0], matchPositions[match.match][1])
    }
    
    context.lineWidth = dis(4)
    context.lineCap = "butt"
    context.strokeStyle = "#000000"
    context.beginPath()
    for (var i = 0; i < matchData.length; i++ ) {
        match = matchData[i]
        for (var f = 0; f < match.inputs.length; f++ ) {
            startX = matchPositions[match.match][0]
            startY = matchPositions[match.match][1]
            endX = matchPositions[match.inputs[f]][0]
            endY  = matchPositions[match.inputs[f]][1]
            function checkMatch(testMatch) {
                return (testMatch.match == match.inputs[f])
            }
            targetMatch = matchData.find(checkMatch)
            if (targetMatch.column < 0) {
                startX -= 200
                endX += 200
            } else {
                startX += 200
                endX -= 200
            }
            
            context.moveTo(x(startX), y(startY))
            context.lineTo(x(((endX - startX) / 2) + startX), y(startY))
            context.lineTo(x(((endX - startX) / 2) + startX), y(endY))
            context.lineTo(x(endX), y(endY))
        }
    }
    context.stroke()
}
