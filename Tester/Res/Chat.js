class Chat {

    static Data = null

    static SetLeft

    static LastGen_GenCountdown = 2

    static modal_EditGenerated = null

    static div_Output_LineInOption = null

    static GenerateConfig = {
        top_p: 0.7,
        top_k: 0,
        temperature: 2,
        presence_penalty: 0.5,
        frequency_penalty: 0.5,
        max_token: 5000,
        turns: 1,
        min_len: 0,
        options: 5
    }

    static isEditor = false

    static Init(isEditor) {
        Chat.isEditor = isEditor
        M.AutoInit()
        Chat.modal_EditGenerated = M.Modal.init(document.getElementById("modal_EditGenerated"))
        Chat.div_Output_LineInOption = document.getElementById("div_Output_LineInOption")
        if (isEditor) {
            document.getElementById("ipt_Chat_Message_0").onkeydown = (e) => {
                let event = e || window.event
                let key = event.which || event.keyCode || event.charCode
                if (key == 13) Chat.UI_Chat(0)

            }
            document.getElementById("ipt_Chat_Message_1").onkeydown = (e) => {
                let event = e || window.event
                let key = event.which || event.keyCode || event.charCode
                if (event.ctrlKey && key == 13) Chat.UI_Chat(1)
            }
            document.getElementById("ipt_Chat_Message_Generate").onkeydown = (e) => {
                let event = e || window.event
                let key = event.which || event.keyCode || event.charCode
                if (event.ctrlKey && key == 13) Chat.UI_StartGenerate(true)
            }
            document.getElementById("ipt_Chat_Message_EditGenerated").onkeydown = (e) => {
                let event = e || window.event
                let key = event.which || event.keyCode || event.charCode
                if (event.ctrlKey && key == 13) Chat.UI_ApplyGeneratedOption_AdvModal()
            }
        }
        Chat.ForceRefresh()
    }

    static LoadPrompt(ID) {
        Chat.Data = TestData.Data[ID]
        let AppStartRequest = new Request(
            "/API/NewChat", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(Chat.Data)
        })
        fetch(AppStartRequest).then(
            res => {
                res.json().then(
                    json => {
                        if (json.code = 200) {
                            Chat.UI_LoadCharacters()
                            Chat.ForceRefresh()
                        }
                    })
            }).then(

        )
    }

    static Chat(ChatLine, GenerateNow = false) {
        if (ChatLine.Message.length != "") {

            let AppStartRequest = new Request(
                "/API/NewMessage", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(ChatLine)
            })
            fetch(AppStartRequest).then(
                res => {
                    res.json().then(
                        json => {
                            if (json.code = 200) {
                                Chat.UI_MakeLine(ChatLine, document.getElementById("div_Output_Pending"))
                                Chat.UI_ClearMsg()
                                Chat.UI_GoBottom()
                            }
                        })
                }).then(

            )
        }
    }

    static StartGenerate(Data) {
        let AppStartRequest = new Request(
            "/API/StartGenerate", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(Data)
        })
        this.UI_MakeGeneratedOption()
        fetch(AppStartRequest).then(
            res => {
                res.json().then(
                    json => {
                        if (json.code = 200) {
                            Chat.UI_InsertGeneratedOption(json.Data.Reply, json.Data.Request)
                            if (Chat.LastGen_GenCountdown > 0) {
                                Chat.LastGen_GenCountdown--
                                Chat.GenerateAgain()
                            }
                        }
                    })
            }).then()
    }

    static GenerateAgain() {
        let AppStartRequest = new Request(
            "/API/GenerateAgain", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        })
        this.UI_MakeGeneratedOption()
        fetch(AppStartRequest).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        Chat.UI_InsertGeneratedOption(json.Data.Reply, json.Data.Request)
                        if (Chat.LastGen_GenCountdown > 0) {
                            Chat.LastGen_GenCountdown--
                            Chat.GenerateAgain()
                        }
                    }
                })
            }).then()
    }

    static UndoLine() {
        fetch(new Request("/API/UndoLine")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        Chat.ForceRefresh()
                    }
                })
            })
    }

    static SaveAndContinue() {
        fetch(new Request("/API/SaveAndContinue")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        document.getElementById("div_Output_Confirmed").innerHTML += document.getElementById("div_Output_Pending").innerHTML
                        document.getElementById("div_Output_Pending").innerHTML = ""
                    }
                })
            })
    }

    static SaveToLog() {
        fetch(new Request("/API/SaveToLog")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        document.getElementById("div_Output_Confirmed").innerHTML += document.getElementById("div_Output_Pending").innerHTML
                        document.getElementById("div_Output_Pending").innerHTML = ""
                    }
                })
            })
    }

    static NoGoodBackAgain() {
        fetch(new Request("/API/NGBackAgain")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        Chat.ForceRefresh()
                    }
                })
            })
    }

    static UndoLine() {
        fetch(new Request("/API/UndoLine")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        Chat.ForceRefresh()
                    }
                })
            })
    }

    static ForceRefresh() {
        document.getElementById("div_Output_Confirmed").innerHTML = ""
        if (Chat.isEditor) document.getElementById("div_Output_Pending").innerHTML = ""
        fetch(new Request("/API/Refresh")).then(
            res => {
                res.json().then(json => {
                    if (json.code = 200) {
                        if (Chat.Data == null) {
                            Chat.Data = json.Data
                            Chat.UI_LoadCharacters()
                        }
                        Chat.Lines = json.Data
                        json.Data.History.forEach(line =>
                            Chat.UI_MakeLine(line, document.getElementById("div_Output_Confirmed")))
                        json.Data.Pending.forEach(line =>
                            Chat.UI_MakeLine(line, document.getElementById("div_Output_Pending")))
                        Chat.UI_GoBottom()
                    }
                })
            })
    }

    static UI_GetAvatarURL(CharacterName) {
        return `/Save/${Chat.Data.ScenarioSeries}/${Chat.Data.ScenarioName}/${CharacterName}.png`
    }

    static UI_GetAvatar(CharacterName) {
        return `<div class="Avatar"><i>${CharacterName}</i><img class="Avatar" src="${Chat.UI_GetAvatarURL(CharacterName)}" onerror="this.style.display='none'"/><div>`
    }

    static UI_Chat(InputIndex) {
        let Data = {
            "Message": Chat.UI_GetMsg(InputIndex),
            "InputTag": "用户输入",
            "Character": Chat.UI_GetMsgFrom(InputIndex)
        }
        Chat.Chat(Data, InputIndex == 0)
        if (InputIndex == 0) Chat.UI_StartGenerate(false)
    }

    static UI_StartGenerate(UseAvdCtrl) {
        Chat.LastGen_GenCountdown = Chat.GenerateConfig.options - 1
        let Data = {
            Character: Chat.Data.Characters.AI[0],
            StartWith: "",
            Lines: 1,
            MinLength: 0,
            Cfg: Chat.GenerateConfig
        }
        if (UseAvdCtrl) {
            Data.Character = document.getElementById("slct_Chat_MessageFrom_Generate").value
            Data.StartWith = document.getElementById("ipt_Chat_Message_Generate").value
        }
        Chat.UI_MakePendingLine(Data.Character)
        Chat.StartGenerate(Data)
    }

    static UI_GenerateMore() {
        Chat.LastGen_GenCountdown = Chat.GenerateConfig.options
        Chat.GenerateAgain()
    }

    static UI_MakeLine(LineData, Parent) {
        let Elmt = document.createElement("div")
        Elmt.classList.add("Message")
        Elmt.setAttribute("tag", LineData.InputTag)
        if (LineData.Character == null || LineData.Character == "系统提示")
            Elmt.setAttribute("character", "System")
        else if (LineData.Character == "" || LineData.Character == "旁白")
            Elmt.setAttribute("character", "Narrator")
        else if (Chat.SetLeft.has(LineData.Character)) {
            Elmt.setAttribute("character", "AI")
            Elmt.innerHTML += Chat.UI_GetAvatar(LineData.Character)
        } else {
            Elmt.setAttribute("character", "User")
            Elmt.innerHTML += Chat.UI_GetAvatar(LineData.Character)
        }
        Elmt.innerHTML +=
            `<div class="Content">${LineData.Message.replace(/\n/g, "<br/>")}</div>`
        if (LineData.InputTag == "模型生成")
            Elmt.innerHTML +=
                ``
        Parent.append(Elmt)
    }

    static UI_MakePendingLine(Character) {
        if (Chat.div_Output_LineInOption.children.length == 0) {
            let Elmt = document.createElement("div")
            Elmt.classList.add("Message")
            if (Character == null || Character == "系统提示")
                Elmt.setAttribute("character", "System")
            else if (Character == "" || Character == "旁白")
                Elmt.setAttribute("character", "Narrator")
            else if (Chat.SetLeft.has(Character)) {
                Elmt.setAttribute("character", "AI")
                Elmt.innerHTML += Chat.UI_GetAvatar(Character)
            } else {
                Elmt.setAttribute("character", "User")
                Elmt.innerHTML += Chat.UI_GetAvatar(Character)
            }
            Elmt.innerHTML += `<div class="Content"><ul id="GeneratedSelecter" class=""><li class="More"><a class="waves-effect btn-flat" onclick='Chat.UI_GenerateMore()'>更多</a></li></ul></div>`
            Chat.div_Output_LineInOption.append(Elmt)
        }
    }

    static UI_ClearPendingLine() {
        Chat.div_Output_LineInOption.innerHTML = ""
        Chat.UI_GoBottom()
    }

    static UI_LoadCharacters() {
        Chat.SetLeft = new Set(Chat.Data.Characters.AI)
        if (Chat.isEditor) {
            document.getElementById("div_SimpleChat_UserName").innerText = `${Chat.Data.Characters.User[0]}：`
            let Elmts = document.querySelectorAll("select.CharacterSelecter optgroup.User")
            Elmts.forEach(elmt =>
                Chat.Data.Characters.User.forEach(name => {
                    elmt.innerHTML += `<option value="${name}" data-icon="${Chat.UI_GetAvatarURL(name)}">${name}</option>`
                }))
            Elmts = document.querySelectorAll("select.CharacterSelecter optgroup.AI")
            Elmts.forEach(elmt =>
                Chat.Data.Characters.AI.forEach(name => {
                    elmt.innerHTML += `<option value="${name}" data-icon="${Chat.UI_GetAvatarURL(name)}">${name}</option>`
                }))
            M.FormSelect.init(document.querySelectorAll('select'))
        }
    }

    static UI_MakeGeneratedOption() {
        let Elmt = document.createElement("li")
        Elmt.classList.add("btn-flat")
        Elmt.classList.add("waves-effect")
        Elmt.setAttribute("type", "Generating")
        Elmt.innerHTML = Chat.val_PendingPreLoader
        document.getElementById("GeneratedSelecter").append(Elmt)
        console.log("!")
    }

    static UI_InsertGeneratedOption1(LineText, Request) {
        LineText = Request.StartWith + LineText
        let Elmt = document.querySelector("#GeneratedSelecter>li[type='Generating']")
        Elmt.setAttribute("type", "Generated")
        Elmt.innerHTML =
            `<div class="Content"  onclick='Chat.UI_ApplyGeneratedOption("${LineText}","${Request.Character}")'>${LineText}</div>
            <a class="btn waves-effect deep-purple lighten-2" onclick='Chat.UI_EditGenerated("${LineText}","${Request.Character}")'>编辑</a>`
        document.getElementById("GeneratedSelecter").append(Elmt)
    }

    static UI_InsertGeneratedOption(LineText, Request) {
        LineText = Request.StartWith + LineText
        let Elmt = document.querySelector("#GeneratedSelecter>li[type='Generating']")
        if (Elmt != null) {
            Elmt.setAttribute("type", "Generated")
            Elmt.innerHTML = ""
            let Content = document.createElement("div")
            Content.classList.add("Content")
            Content.innerText = LineText
            Content.onclick = () => Chat.UI_ApplyGeneratedOption(LineText, Request.Character)
            Elmt.append(Content)
            let btn = document.createElement("a")
            btn.classList.add("btn")
            btn.classList.add("waves-effect")
            btn.classList.add("deep-purple")
            btn.classList.add("lighten-2")
            btn.innerText = "编辑"
            btn.onclick = () => Chat.UI_EditGenerated(LineText, Request.Character)
            Elmt.append(btn)
            Chat.UI_GoBottom()
        }
        else Chat.LastGen_GenCountdown = 0
    }

    static UI_ApplyGeneratedOption(GeneratedLine, Character) {
        let Data = {
            "Message": GeneratedLine,
            "InputTag": "模型生成",
            "Character": Character
        }
        Chat.Chat(Data, false)
        Chat.UI_ClearPendingLine()
    }

    static UI_ApplyGeneratedOption_AdvModal() {
        let Data = {
            "Message": document.getElementById("ipt_Chat_Message_EditGenerated").value,
            "InputTag": "模型生成(人工编辑)",
            "Character": document.getElementById(`slct_Chat_MessageFrom_EditGenerated`).value
        }
        Chat.Chat(Data, false)
        Chat.UI_ClearPendingLine()
        Chat.modal_EditGenerated.close()
    }

    static UI_GoBottom() {
        document.querySelector("#div_Output .ControlPanel").scrollIntoView({
            behavior: "smooth",
            block: "end",
            inline: "end"
        })
    }

    static UI_GetMsgFrom(InputIndex) {
        if (InputIndex > 0)
            return document.getElementById(`slct_Chat_MessageFrom_${InputIndex}`).value
        else if (InputIndex == 0)
            return Chat.Data.Characters.User[0]
    }

    static UI_GetMsg(InputIndex) {
        return document.getElementById(`ipt_Chat_Message_${InputIndex}`).value
    }

    static UI_ClearMsg() {
        document.querySelectorAll("div.input-field .Chat_Message").forEach((ipt) => ipt.value = "")
    }

    static UI_GetMsg(Index) {
        if (Index == -1) return document.querySelector("#ipt_Chat_Message").value
        else return document.querySelectorAll("div.input-field .Chat_Message")[Index].value
    }

    static UI_EditGenerated(GeneratedLine, GeneratedCharacter) {
        document.getElementById("ipt_Chat_Message_EditGenerated").value = GeneratedLine
        document.getElementById(`slct_Chat_MessageFrom_EditGenerated`).value = GeneratedCharacter
        M.updateTextFields()
        Chat.modal_EditGenerated.open()
    }

    static val_PendingPreLoader = `<div class="preloader-wrapper small active"><div class="spinner-layer spinner-white-only"><div class="circle-clipper left"><div class="circle"></div></div><div class="gap-patch"><div class="circle"></div></div><div class="circle-clipper right"><div class="circle"></div></div></div></div>`
}