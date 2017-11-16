const field_names = ["hostname", "port", "web_port", "username", "password"]
letquitting = false

// Create a web socket.
let soc = null
let output = document.getElementById("output")

output.onkeydown = (e) => {
    modifiers = []
    for (name of ["ctrl", "shift", "alt"]) {
        if (e[`${name}Key`]) {
            modifiers.push(name)
        }
    }
    key = e.key.toUpperCase()
    if (key != "F5" && key != "ALT") {
        e.preventDefault()
    }
    send({name: "key", args: [key, modifiers]})
}

let connect_form = document.getElementById("connect-form")
let connect = document.getElementById("connect")

for (name of field_names) {
    value = Cookies.get(name)
    if (value !== undefined) {
        document.getElementById(name).value = value
    }
}

let game = document.getElementById("game")
let url = document.getElementById("url")

url.onclick = (e) => {
    url.hidden = true
}

let menu = document.getElementById("menu")
let menu_h = document.getElementById("menu-h")
let menu_p = document.getElementById("menu-p")
let menu_hide = document.getElementById("menu-hide")
menu_hide.onclick = (e) => {
    menu.hidden = true
}

let text = document.getElementById("text")

let text_cancel = document.getElementById("text-cancel")
text_cancel.onclick = (e) => {
    text.hidden = true
}

let text_h = document.getElementById("text-h")
let text_form = document.getElementById("text-form")
let text_element = null

let text_command = {
    name: null,
    args: [],
    kwargs: {}
}

text_form.onsubmit = (e) => {
    e.preventDefault()
    text_command.args.push(text_element.value)
    send(text_command)
    text.hidden = true
}

let text_label = document.getElementById("text-label")
let text_field = document.getElementById("text-field")

let form = document.getElementById("form")
let form_h = document.getElementById("form-h")
let form_p = document.getElementById("form-p")
let form_hide = document.getElementById("form-hide")
form_hide.onclick = (e) => {
    form.hidden = true
}
let form_ok = document.getElementById("form-ok")

for (element of document.getElementsByClassName("hidden")) {
    element.hidden = true
}

document.getElementById("disconnect").onclick = (e) => {
    send({name: "quit"})
}

function set_title(name) {
    title = document.title.slice(0, document.title.search(/[|] /) + 2)
    if (name === undefined) {
        name = "Client"
    }
    document.title = `${title}${name}`
}

function write_message(text) {
    e = document.createElement("p")
    e.innerText = text
    output.appendChild(e)
}

function write_special(text) {
    write_message(`--- ${text} ---`)
}

// All the objects the client knows about.
objects = {}

mindspace_functions = {
    random_sound: (obj) => {
    },
    object_sound: (obj) => {
        let [id, path, sum] = obj.args
    },
    hidden_sound: (obj) => {
        let [path, sum, x, y, z, is_dry] = obj.args
    },
    url: (obj) => {
        let [title, href] = obj.args
        url.hidden = false
        url.innerText = title
        url.href = href
        url.focus()
    },
    get_text: (obj) => {
        let [message, command, value, multiline, escapable, args, kwargs] = obj.args
        text.hidden = false
        text_cancel.focus()
        text_label.innerText = message
        text_command.name = command
        text_command.args = args
        text_command.kwargs = kwargs
        if (multiline) {
            e = document.createElement("textarea")
        } else {
            e = document.createElement("input")
            e.type = "text"
        }
        e.value = value
        text_element = e
        // Below code based on the first answer at:
        // https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
        while (text_field.firstChild) {
            text_field.removeChild(myNode.firstChild);
        }
        text_field.appendChild(e)
        if (escapable) {
            text_form.onkeydown = (e) => {
                if (e.key == "escape") {
                    text.hidden = true
                    e.preventDefault
                }
            }
        } else {
            text_form.onkeydown = null
        }
    },
    form: (obj) => {
        let [title, fields, command, args, kwargs, ok, cancel] = obj.args
        form.hidden = false
        form_h.innerText = title
        form_hide.innerText = cancel
        form_hide.focus()
    },
    menu: (obj) => {
        let [title, items, escapable] = obj.args
        for (element of [menu_h, menu_p]) {
            element.innerText = ""
        }
        menu.hidden = false
        menu_h.innerText = title
        menu_hide.focus()
        for (item of items) {
            let [name, command, args, kwargs] = item
            p = document.createElement("p")
            if (command) {
                i = document.createElement("input")
                i.type = "button"
                i.value = name
                i.command = command
                i.args = JSON.stringify(args)
                i.kwargs = JSON.stringify(kwargs)
                i.onclick = (e) => {
                    i = e.target
                    send(
                        {
                            name: i.command,
                            args: JSON.parse(i.args),
                            kwargs: JSON.parse(i.kwargs)
                        }
                    )
                    menu.hidden = true
                }
            } else {
                i = document.createElement("h2")
                i.text = name
            }
            p.appendChild(i)
            menu_p.appendChild(p)
        }
        if (escapable) {
            menu.onkeydown = (e) => {
                if (e.key == "escape") {
                    menu.hidden = true
                    e.preventDefault()
                }
            }
        } else {
            menu.onkeydown = null
        }
    },
    remember_quit: (obj) => {
        quitting = true
    },
    message: (obj) => {write_message(obj.args[0])},
    delete: (obj) => {
        id = obj.args[0]
        delete objects[id]
    },
    identify: (obj) => {
        let [id, x, y, z, ambience_sound, ambience_volume] = obj.args
        objects[id] = {
            x: x, y: y, z: z, ambience_sound: ambience_sound,
            ambience_volue: ambience_volume
        }
        write_message(`Identify #${id}.`)
    },
    interface_sound: (obj) => {
        let [path, sum] = obj.args
        write_message(`Interface sound: ${path}.`)
    },
    character_id: (obj) => {
        id = obj.args[0]
        write_message(`Character: #${id}.`)
    },
    zone: (obj) => {
        let [ambience_sound, background_rate, background_volume] = obj.args
        write_message("I know about zone.")
    },
    location: (obj) => {
        let [name, ambience_sound, ambience_volume, music_sound, max_distance, reverb_options] = obj.args
        write_message("I know about location.")
    },
    options: (obj) => {
        let [username, transmition_id, recording_threshold, sound_volume, ambience_volume, music_volume] = obj.args
        set_title(username)
    },
    mute_mic: (obj) => {void(0)}
}

function send(obj) {
    if (obj.args === undefined) {
        obj.args = []
    }
    if (obj.kwargs === undefined) {
        obj.kwargs = {}
    }
    let l = [obj.name, obj.args, obj.kwargs]
    soc.send(JSON.stringify(l))
}

set_title()

connect_form.onsubmit = (e) => {
    e.preventDefault()
    let obj = {}
    let ok = true
    for (name of field_names) {
        let field = document.getElementById(name)
        if (!field.value) {
            alert(`You must specify a ${name.replace("_", " ")}.`)
            field.focus()
            ok = false
            break
        } else {
            Cookies.set(name, field.value, {expires: 30, path: "/"})
            obj[name] = field.value
        }
    }
    if (ok) {
        create_socket(obj)
    }
    return false
}

function writeMessage(text) {
    document.getElementById("output").innerHTML += `<p>${text}</p>`
}

function create_socket(obj) {
    connect.hidden = true
    game.hidden = false
    soc = new WebSocket(`ws://${obj.hostname}:${obj.port}`)
    soc.onclose = (e) => {
        connect.hidden = false
        set_title()
        if (e.wasClean) {
            reason = "Connection was closed cleanly."
        } else {
            reason = e.reason
        }
        write_special(reason)
    }
    soc.onopen = (e) => {
        output.innerHTML = ""
        write_special("Connection Open")
        send(
            {
                "name": "login",
                "args": [obj.username, obj.password]
            }
        )
    }
    soc.onmessage = (e) => {
        let obj = JSON.parse(e.data)
        let func = mindspace_functions[obj.name]
        if (func !== undefined) {
            func(obj)
        } else {
            write_message(`Unrecognised command: ${e.data}.`)
        }
    }
}
