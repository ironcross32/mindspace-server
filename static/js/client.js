/* global Cookies */

let field_names = ["hostname", "port", "web_port", "username", "password"]
let default_title = document.title

// The audio system:
let audio = null
let mixer = null
let sounds = {}

let reverb = {}
let room_mixer = null
let room = null
let zone = null
let music = null

let escape = null

let quitting = false

function create_ambience(obj, sound, volume, output) {
    if (volume === undefined) {
        volume = 1.0
    }
    if (output === undefined) {
        output = audio.destination
    }
    if (sound === null) {
        if (obj !== null) {
            obj.source.disconnect()
        }
    } else {
        let [path, sum] = sound
        if (obj === null || obj.path != path || obj.sum !== sum) {
            if (obj !== null) {
                obj.source.disconnect()
            }
            get_sound(path, sum).then(get_source).then(source => {
                if (obj.mixer === null) {
                    create_main_mixer()
                    obj.mixer = audio.createGain()
                    obj.mixer.connect(output)
                }
                obj.mixer.gain.value = volume
                obj.path = path,
                obj.sum = sum,
                obj.source = source
                source.loop = true
                source.connect(obj.mixer)
                source.start()
            })
        }
    }
    return obj
}

function create_mixer(volume, output) {
    let g = audio.createGain()
    if (volume !== null && volume !== undefined) {
        g.gain.value = volume
    }
    if (output !== null) { // Optionally don't connect this node.
        if (output === undefined) {
            output = audio.destination
        }
        g.connect(output)
    }
    return g
}

function create_main_mixer() {
    if (mixer === null) {
        mixer = create_mixer(player.sound_volume)
    }
}

function stop_object_ambience(thing) {
    if (thing.ambience !== null && thing.ambience !== undefined) {
        if (thing.ambience.source !== null && thing.ambience.source !== undefined) {
            thing.ambience.source.disconnect()
        }
        thing.ambience = null
    }
}

function get_sound(path, sum) {
    return new Promise(
        (resolve, reject) => {
            if (sounds[path] !== undefined && sounds[path].sum == sum) {
                let sound = sounds[path]
                if (sound.downloading) {
                    return reject("Sound has not been downloaded.")
                } else {
                    return resolve(sound)
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
                url = `http://${hostname}:${port}/${path}?${sum}`
                // Below code modified from:
                // https://www.html5rocks.com/en/tutorials/webaudio/intro/
                let request = new XMLHttpRequest()
                request.open("GET", url)
                request.responseType = "arraybuffer"
                // Decode asynchronously
                request.onerror = () => reject(`Failed to download sound from ${url}.`)
                request.onload = () => {
                    audio.decodeAudioData(request.response, (buffer) => {
                        sound.downloading = false
                        sound.buffer = buffer
                        resolve(sound)
                    }, () => {
                        reject(`Unable to decode data from ${url}.`)
                    })
                }
                request.send()
            }
        }
    )
}

function get_source(sound) {
    return new Promise((resolve, reject) => {
        if (sound.downloading) {
            reject("Sound has not yet been downloaded.")
        } else {
            let source = audio.createBufferSource()
            source.buffer = sound.buffer
            resolve(source)
        }
    })
}

function play_sound(path, sum) {
    get_sound(path, sum).then(get_source).then(source => {
        create_main_mixer()
        source.connect(mixer)
        source.start(0)
    })
}

function send(obj) {
    if (obj.args === undefined) {
        obj.args = []
    }
    if (obj.kwargs === undefined) {
        obj.kwargs = {}
    }
    let l = [obj.name, obj.args, obj.kwargs]
    let value = JSON.stringify(l)
    soc.send(value)
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
    random_sound: obj => {
        let [path, sum] = obj.args
        play_sound(path, sum)
    },
    object_sound: obj => {
        let [id, path, sum] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            send({name: "identify", args: [id]})
        } else {
            play_sound(path, sum)
        }
    },
    hidden_sound: () => {
        // let [path, sum, x, y, z, is_dry] = obj.args
        // sound = get_sound(path, sum)
    },
    url: obj => {
        let [title, href] = obj.args
        url.hidden = false
        escape = url
        url.innerText = title
        url.href = href
        url.focus()
    },
    get_text: obj => {
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
    form: obj => {
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
    menu: obj => {
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
    message: obj => {write_message(obj.args[0])},
    delete: obj => {
        let id = obj.args[0]
        if (objects[id] !== undefined) {
            stop_object_ambience(objects[id])
            delete objects[id]
        }
    },
    identify: obj => {
        let [id, x, y, z, ambience_sound, ambience_volume] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            thing = {ambience_sound: null, ambience_mixer:null}
            objects[id] = thing
        }
        thing.x = x
        thing.y = y
        thing.z = z
        if (ambience_sound === null) {
            stop_object_ambience(thing)
        } else {
            let [path, sum] = ambience_sound
            if (thing.ambience === null || thing.ambience.path != path || thing.ambience.sum != sum) {
                stop_object_ambience(thing)
                get_sound(path, sum).then(get_source).then(source => {
                    if (thing.ambience == null) {
                        // Nobody has got here first.
                        if (thing.ambience_mixer === null) {
                            thing.ambience_mixer = create_mixer(ambience_volume)
                        } else {
                            thing.ambience_mixer.gain.value = ambience_volume
                        }
                        source.connect(thing.ambience_mixer)
                        source.loop = true
                        source.start(0)
                        thing.ambience = {
                            path: path,
                            sum: sum,
                            source: source
                        }
                    }
                })
            }
        }
    },
    interface_sound: obj => {
        let [path, sum] = obj.args
        play_sound(path, sum)
    },
    character_id: obj => {
        let id = obj.args[0]
        write_message(`Character: #${id}.`)
    },
    zone: obj => {
        let [ambience_sound, background_rate, background_volume] = obj.args
        if (ambience_sound !== null) {
            let sound = get_sound(...ambience_sound)
            write_special(`Zone sound: ${sound}: ${background_rate}, ${background_volume}.`)
        }
        write_message("I know about zone.")
    },
    location: obj => {
        let [name, ambience_sound, ambience_volume, music_sound, max_distance, reverb_options] = obj.args
        reverb.options = reverb_options
        reverb.max_distance = max_distance
        if (room_mixer === null) {
            room_mixer = create_mixer(player.ambience_volume)
        }
        music = create_ambience(music, music_sound, player.music_volume)
        room = create_ambience(room, ambience_sound, ambience_volume, room_mixer)
        room.name = name
    },
    options: obj => {
        let [username, transmition_id, recording_threshold, sound_volume, ambience_volume, music_volume] = obj.args
        set_title(username)
        player.name = username
        player.transmition_id = transmition_id
        player.recording_threshold = recording_threshold
        player.sound_volume = sound_volume
        if (mixer !== null) {
            mixer.gain.value = sound_volume
        }
        player.ambience_volume = ambience_volume
        if (room !== null) {
            room.mixer.gain.value = ambience_volume
        }
        player.music_volume = music_volume
        if (music !== null) {
            music.mixer.gain.value = music_volume
        }
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
