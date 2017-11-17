/* global Cookies */

let field_names = ["hostname", "port", "web_port", "username", "password"]
let default_title = document.title

// The audio system:
let audio = null
let sounds = {}

let escape = null

let quitting = false

function get_sound(path, sum) {
    if (sounds[path] !== undefined && sounds[path].sum == sum) {
        let sound = sounds[path]
        if (sound.downloading) {
            return null
        } else {
            return sound
        }
    } else {
        let sound = {
            path: path,
            sum: sum,
            downloading: true
        }
        sounds[path] = sound
        let hostname = document.getElementById("hostname").value
        let port = document.getElementById("web_port").value
        url = `${hostname}:${port}${path}?${sum}`
        // Below code modified from:
        // https://www.html5rocks.com/en/tutorials/webaudio/intro/
        let request = new XMLHttpRequest()
        request.open("GET", url, true)
        request.responseType = "arraybuffer"
        // Decode asynchronously
        request.onload = () => {
            audio.decodeAudioData(
                request.response, (buffer) => {
                    let source = audio.createBufferSource()
                    sound.source = source
                    sound.downloading = false
                    source.buffer = buffer
                    source.connect(audio.destination)
                    source.start(0)
                }, () => {
                    alert(`Unable to decode data from ${url}.`)
                }
            )
        }
        request.send()
        return sound
    }
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

// Create a web socket.
let soc = null
let connected = false

// Page elements.

let output = document.getElementById("output")
document.onkeydown = (e) => {
    let current = document.activeElement
    if (
        connected && [
            "text", "password", "textarea", "number", "select-one"
        ].indexOf(current.type) == -1
    ) {
        let modifiers = []
        for (let name of ["ctrl", "shift", "alt"]) {
            if (e[`${name}Key`]) {
                modifiers.push(name)
            }
        }
        let key = e.key.toUpperCase()
        if (!modifiers.count && key == "ESCAPE" && escape !== null) {
            escape.hidden = true
            escape = null
        } else {
            if (key == "TAB" || key[0] == "F") {
                e.preventDefault()
            }
            send({name: "key", args: [key, modifiers]})
        }
    }
}

let connect_form = document.getElementById("connect-form")
let connect = document.getElementById("connect")

for (let name of field_names) {
    let value = Cookies.get(name)
    if (value !== undefined) {
        document.getElementById(name).value = value
    }
}

let game = document.getElementById("game")
let url = document.getElementById("url")

url.onclick = () => {
    url.hidden = true
}

let menu = document.getElementById("menu")
let menu_h = document.getElementById("menu-h")
let menu_div = document.getElementById("menu-div")
let menu_hide = document.getElementById("menu-hide")
menu_hide.onclick = () => {
    menu.hidden = true
}

let text = document.getElementById("text")

let text_cancel = document.getElementById("text-cancel")
text_cancel.onclick = () => {
    text.hidden = true
}

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

form.onsubmit = (e) => {
    e.preventDefault()
    let data = {}
    for (let name in form_fields) {
        let field = form_fields[name]
        let value = field.value
        if (field.type == "select-one" && !value) {
            value = null
        }
        data[name] = value
    }
    form_command.args.push(data)
    send(form_command)
    form.hidden = true
}

let form_h = document.getElementById("form-h")
let form_p = document.getElementById("form-p")
let form_hide = document.getElementById("form-hide")
form_hide.onclick = () => {
    form.hidden = true
}
let form_ok = document.getElementById("form-ok")

let form_command = {
    name: null,
    args: [],
    kwargs: {}
}
let form_fields = {}

hide_elements()

document.getElementById("disconnect").onclick = () => {
    if (connected) {
        send({name: "quit"})
    } else {
        alert("You are not connected.")
    }
}

function menu_button(e) {
    escape = null
    let i = e.target
    send(
        {
            name: i.command,
            args: JSON.parse(i.args),
            kwargs: JSON.parse(i.kwargs)
        }
    )
    menu.hidden = true
}

function clear_element(e) {
    // Below code based on the first answer at:
    // https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
    while (e.firstChild) {
        e.removeChild(e.firstChild)
    }
}

function hide_elements() {
    for (let element of document.getElementsByClassName("hidden")) {
        element.hidden = true
    }
}

function set_title(name) {
    let title = default_title
    if (name !== undefined) {
        title = `${title} (${name})`
    }
    document.title = title
}

function write_message(text) {
    let e = document.createElement("p")
    e.innerText = text
    output.appendChild(e)
}

function write_special(text) {
    write_message(`--- ${text} ---`)
}

// All the objects the client knows about:
let objects = {}

// The current player object:
let player = {
    name: null,
    transmition_id: null,
    recording_threshold: null,
    sound_volume: null,
    ambience_volume: null,
    music_volume: null
}

let mindspace_functions = {
    random_sound: () => {
    },
    object_sound: (obj) => {
        let [id, path, sum] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            send({name: "identify", args: [id]})
        } else {
            let sound = get_sound(path, sum)
            write_special(sound)
        }
    },
    hidden_sound: () => {
        // let [path, sum, x, y, z, is_dry] = obj.args
        // sound = get_sound(path, sum)
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
        if (escapable) {
            escape = text
        }
        text_label.innerText = message
        text_command.name = command
        text_command.args = args
        text_command.kwargs = kwargs
        let e = null
        if (multiline) {
            e = document.createElement("textarea")
        } else {
            e = document.createElement("input")
            e.type = "text"
        }
        e.value = value
        text_element = e
        clear_element(text_field)
        text_field.appendChild(e)
        e.focus()
    },
    form: (obj) => {
        let [title, fields, command, args, kwargs, ok, cancel] = obj.args
        form.hidden = false
        form_h.innerText = title
        form_ok.innerText = ok
        if (cancel !== null) {
            form_hide.innerText = cancel
            escape = form
        }
        form_hide.focus()
        clear_element(form_p)
        form_command = {
            name: command,
            args: args,
            kwargs: kwargs
        }
        form_fields = {}
        for (let data of fields) {
            let i = null
            if (data.type == "Label") {
                i = document.createElement("h3")
                i.innerText = data.values[0]
            } else {
                let [name, value, type, title, hidden] = data.values
                let empty = ""
                let e = null
                if (type == "text") {
                    e = document.createElement("textarea")
                } else if (typeof(type) != "string") {
                    e = document.createElement("select")
                    for (let key in type) {
                        let v = document.createElement("option")
                        if (Array.isArray(type)) {
                            v.value = type[key]
                        } else {
                            v.value = key
                        }
                        v.innerText = type[key]
                        e.appendChild(v)
                    }
                } else {
                    e = document.createElement("input")
                    if (type == "float" || type == "int") {
                        e.type = "number"
                        let step = null
                        if (type == "int") {
                            step = "1"
                            empty = "0"
                        } else {
                            step = "0.1"
                            empty = "0.0"
                        }
                        e.step = step
                    } else {
                        if (hidden) {
                            e.type = "password"
                        } else {
                            e.type = "text"
                        }
                    }
                }
                e.value = value || empty
                i = document.createElement("label")
                let s = document.createElement("span")
                s.innerText = `${title} `
                i.appendChild(s)
                i.appendChild(e)
                form_fields[name] = e
            }
            form_p.appendChild(i)
        }
    },
    menu: (obj) => {
        let [title, items, escapable] = obj.args
        menu.hidden = false
        if (escapable) {
            escape = menu
        }
        menu_h.innerText = title
        menu_hide.focus()
        clear_element(menu_div)
        for (let item of items) {
            let [name, command, args, kwargs] = item
            let i = null
            if (command) {
                i = document.createElement("p")
                let e = document.createElement("input")
                e.type = "button"
                e.value = name
                e.command = command
                e.args = JSON.stringify(args)
                e.kwargs = JSON.stringify(kwargs)
                e.onclick = menu_button
                i.appendChild(e)
            } else {
                i = document.createElement("h3")
                i.innerText = name
            }
            menu_div.appendChild(i)
        }
    },
    remember_quit: () => {
        quitting = true
    },
    message: (obj) => {write_message(obj.args[0])},
    delete: (obj) => {
        let id = obj.args[0]
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
        let sound = get_sound(path, sum)
        write_message(`Interface sound: ${sound}.`)
    },
    character_id: (obj) => {
        let id = obj.args[0]
        write_message(`Character: #${id}.`)
    },
    zone: (obj) => {
        let [ambience_sound, background_rate, background_volume] = obj.args
        if (ambience_sound !== null) {
            let sound = get_sound(...ambience_sound)
            write_special(`Zone sound: ${sound}: ${background_rate}, ${background_volume}.`)
        }
        write_message("I know about zone.")
    },
    location: () => {
        // let [name, ambience_sound, ambience_volume, music_sound, max_distance, reverb_options] = obj.args
    },
    options: (obj) => {
        let [username, transmition_id, recording_threshold, sound_volume, ambience_volume, music_volume] = obj.args
        set_title(username)
        player.name = username
        player.transmition_id = transmition_id
        player.recording_threshold = recording_threshold
        player.sound_volume = sound_volume
        player.ambience_volume - ambience_volume
        player.music_volume = music_volume
    },
    mute_mic: () => {}
}

set_title()

connect_form.onsubmit = (e) => {
    e.preventDefault()
    let obj = {}
    let ok = true
    for (let name of field_names) {
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

function create_socket(obj) {
    connect.hidden = true
    game.hidden = false
    soc = new WebSocket(`ws://${obj.hostname}:${obj.port}`)
    soc.onclose = (e) => {
        audio.close()
        if (quitting) {
            connected = false
            connect.hidden = false
            set_title()
            let reason = null
            if (e.wasClean) {
                reason = "Connection was closed cleanly."
            } else {
                reason = `Connection failed: ${e.reason}.`
            }
            write_special(reason)
        } else {
            create_socket(obj)
        }
    }
    soc.onopen = () => {
        connected = true
        let AudioContext = window.AudioContext || window.webkitAudioContext
        audio = new AudioContext()
        clear_element(output)
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
