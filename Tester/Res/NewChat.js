class NewChat {

    static StringFilter(Str) {
        let Rtn = Str.replace(/ /g, '')
        Rtn = Rtn.replace(/:/g, '：')
        Rtn = Rtn.replace(/：/g, ': ')
        return Rtn
    }

    static LoadPrompt() {
        document.getElementById("txtara_Prompt").value = NewChat.StringFilter(document.getElementById("txtara_Prompt").value)
        document.getElementById("txtara_Example").value = NewChat.StringFilter(document.getElementById("txtara_Example").value)
        let AppStartRequest = new Request(
            "/API/NewChat", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(
                {
                    "ScenarioSeries": document.getElementById("ipt_ScenarioSeries").value,
                    "ScenarioName": document.getElementById("ipt_ScenarioName").value,
                    "Prompt": document.getElementById("txtara_Prompt").value,
                    "Example": document.getElementById("txtara_Example").value,
                    "CharacterData": {
                        "AI": (M.Chips.getInstance(document.getElementById("chips_AI")).chipsData).map(e => e.tag),
                        "User": (M.Chips.getInstance(document.getElementById("chips_User")).chipsData).map(e => e.tag)
                    }
                }
            )
        })
        fetch(AppStartRequest).then(
            res => {
                res.json().then(
                    json => {
                        if (json.code = 200) {
                        }
                    })
            }).then(

        )
    }

    static LoadFromJSON() {
        let Jsn = JSON.parse(document.getElementById("txtara_JSON").value)
        document.getElementById("ipt_ScenarioSeries").value = Jsn.ScenarioSeries
        document.getElementById("ipt_ScenarioName").value = Jsn.ScenarioName
        document.getElementById("txtara_Prompt").value = Jsn.Prompt
        document.getElementById("txtara_Example").value = Jsn.Example
        M.updateTextFields()
        M.textareaAutoResize(document.getElementById("txtara_Prompt"))
        M.textareaAutoResize(document.getElementById("txtara_Example"))
    }

    static SendJSON() {
        let AppStartRequest = new Request(
            "/API/NewChat", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: document.getElementById("txtara_JSON").value
        })
        fetch(AppStartRequest).then(
            res => {
                res.json().then(
                    json => {
                        if (json.code = 200) {
                        }
                    })
            }).then(

        )
    }

    static SendLog() {
        let AppStartRequest = new Request(
            "/API/LoadChat", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: document.getElementById("txtara_JSONLog").value
        })
        fetch(AppStartRequest).then(
            res => {
                res.json().then(
                    json => {
                        if (json.code = 200) {
                        }
                    })
            }).then(

        )
    }
}