/* global Cookies, reverbjs */

let field_names = ["username", "password"]
let default_title = document.title
let character_id = null

// The audio system:
let audio = null
let mixer = null
let environment = null
let sounds = {}
let convolvers = {}
let convolver = null
let convolver_url = null
let convolver_mixer = null

let ambience_mixer = null
let room = null
let zone = null
let music = null

let escape = null

let quitting = false

function create_ambience(obj, sound, volume, output) {
    create_environment()
    if (output === undefined) {
        // Let's use the main output.
        output = environment
    }
    if (output === null) {
        // Ambience mixer hasn't been created yet.
        ambience_mixer = audio.createGain()
        ambience_mixer.connect(environment)
        ambience_mixer.gain.value = player.ambience_volume
        output = ambience_mixer
    }
    if (volume === undefined) {
        volume = 1.0 // Full volume.
    }
    if (sound === null) {
        // Silence any existing ambience.
        if (obj !== null) {
            // There's an object of some kind.
            if (obj.source !== null && obj.source !== undefined) {
                // And it has a source; it's been playing.
                obj.source.disconnect()
            }
            obj = {mixer: obj.mixer} // Default object.
        }
    } else {
        // We have a sound to play.
        let [path, sum] = sound
        if (obj === null || obj.path != path || obj.sum !== sum) {
            // Empty object or path and / or sum don't match.
            if (obj !== null) {
                // Could be an old ambience.
                if (obj.source !== undefined) {
                    // There is a sound.
                    obj.source.disconnect()
                }
            } else {
                // Object === null.
                obj = {} // Default object.
            }
            get_sound(path, sum).then(get_source).then(source => {
                if (obj.mixer === null || obj.mixer === undefined) {
                    // Let's build us a mixer.
                    obj.mixer = audio.createGain()
                    obj.mixer.connect(output)
                }
                obj.mixer.gain.value = volume
                obj.path = path,
                obj.sum = sum,
                obj.source = source
                source.loop = true
                source.connect(obj.mixer)
                source.start(0)
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

function create_environment() {
    if (environment === null) {
        environment = create_mixer()
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
                url = `${window.location.href.split(window.location.pathname)[0]}/${path}?${sum}`
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
        create_environment()
        source.connect(environment)
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

// Below code to make Web Audio work on iOS modified from:
// https://paulbakaus.com/tutorials/html5/web-audio-on-ios/

let audio_unlocked = false

function unlock_audio() {
    if(audio_unlocked) {
        return
    }
    // create empty buffer and play it
    let buffer = audio.createBuffer(1, 1, 22050)
    let source = audio.createBufferSource()
    source.buffer = buffer
    source.connect(audio.destination)
    source.start()
    // by checking the play state after some time, we know if we're really unlocked
    setTimeout(function() {
        if((source.playbackState === source.PLAYING_STATE || source.playbackState === source.FINISHED_STATE)) {
            audio_unlocked = true
        }
    }, 0)
}

window.addEventListener("touchstart", unlock_audio, false)

let keyboard = document.getElementById("keyboard")
let modifiers = {}

function create_key(id, value, type) {
    if (value === undefined) {
        value = id.toUpperCase()
    }
    if (type === undefined) {
        type = "standard"
    } else if (type == "special") {
        id = JSON.stringify(id)
    }
    let k = document.createElement("input")
    k.className = `key-${type}`
    k.id = id
    k.value = value
    if (type == "modifier") {
        let l = document.createElement("label")
        let s = document.createElement("span")
        s.innerText = value
        l.appendChild(s)
        k.type = "checkbox"
        modifiers[id] = k
        l.appendChild(k)
        k = l
    } else {
        k.type = "button"
    }
    return k
}

function create_modifier(id, value) {
    return create_key(id, value, "modifier")
}

function create_td(key) {
    // Add a key to a <td> element."""
    let t = document.createElement("td")
    t.appendChild(key)
    return t
}

function add_keys(row, keys) {
    // Row should be a <tr> element.
    for (let key of keys) {
        let k = create_key(key)
        let t = create_td(k)
        row.appendChild(t)
    }
}

function row() {
    return document.createElement("tr")
}

{
    let r = row()
    add_keys(r, ["ESCAPE", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "DELETE"])
    keyboard.appendChild(r)
    r = row()
    add_keys(r, ["NONE", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BACKSPACE"])
    keyboard.appendChild(r)
    r = row()
    add_keys(r, ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "ENTER"])
    keyboard.appendChild(r)
    r = row()
    add_keys(r, ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "#", "HOME", "PAGEDOWN"])
    keyboard.appendChild(r)
    r = row()
    r.appendChild(create_td(create_modifier("shift", "SHIFT")))
    add_keys(r, ["\\", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "END", "PAGEDOWN"])
    keyboard.appendChild(r)
    r = row()
    r.appendChild(create_td(create_modifier("ctrl")))
    r.appendChild(create_td(create_modifier("alt")))
    for (let [key, value] of [
        ["SPACE", "SPACE"],
        ["I", "North"],
        ["O", "Northeast"],
        ["L", "East"],
        [".", "Southeast"],
        [",", "South"],
        ["M", "Southwest"],
        ["J", "West"],
        ["U", "Northwest"],
        ["F1", "Help"],
        ["TAB", "Next Item"]
    ]) {
        r.appendChild(create_td(create_key(key, value)))
    }
    r.appendChild(create_td(create_key({name: "key", args: ["TAB", ["shift"]]}, "Previous Item", "special")))
    keyboard.appendChild(r)
}

function standard_key(e) {
    // Send a key.
    if (!connected) {
        return
    }
    let mods = []
    for (let name in modifiers) {
        let control = modifiers[name]
        if (control.checked) {
            mods.push(control.id)
            control.checked = false
        }
    }
    let button = e.target
    send({
        name: "key",
        args: [button.id, mods]
    })
}

for (let button of document.querySelectorAll(".key-standard")) {
    button.onclick = standard_key
}

function special_key(e) {
    // Send a special key.
    if (!connected) {
        return
    }
    let button = e.target
    let command = JSON.parse(button.id)
    send(command)
}

for (let button of document.querySelectorAll(".key-special")) {
    button.onclick = special_key
}

let hide_keyboard_button = document.getElementById("hide-keyboard")

function hide_keyboard(value) {
    value = value || false
    keyboard.hidden = value
    hide_keyboard_button.value = `${value ? "Show" : "Hide"} Keyboard`
    Cookies.set("hide_keyboard", value, {expires: 30})
}

hide_keyboard(Cookies.get("hide_keyboard"))

hide_keyboard_button.onclick = () => hide_keyboard(!keyboard.hidden)

document.onkeydown = (e) => {
    let current = document.activeElement
    if (e.key === undefined || !connected || [
        "text", "password", "textarea", "number", "select-one"
    ].includes(current.type)) {
        return
    }
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
let menu_ul = document.getElementById("menu-ul")
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
        let value = null
        if (field.type == "select-one") {
            value = field.values[field.value]
        } else if (field.type == "checkbox") {
            value = field.checked
        } else {
            value = field.value || null
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
    // Below code copied from:
    // https://stackoverflow.com/questions/11715646/scroll-automatically-to-the-bottom-of-the-page
    window.scrollTo(0,document.body.scrollHeight)
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
    music_volume: null,
    max_distance: 150
}

function set_convolver(url, node, volume) {
    if (convolver_mixer === null) {
        convolver_mixer = audio.createGain()
        convolver_mixer.connect(audio.destination)
    }
    if (url == convolver_url) {
        node.connect(convolver_mixer)
        convolver_mixer.gain.value = volume
        mixer.connect(node)
        if (node !== convolver) {
            if (convolver !== null) {
                mixer.disconnect(convolver)
                try {
                    convolver.disconnect(convolver_mixer)
                }
                catch (e) {
                    // It was not connected in the first place.
                }
            }
            convolver = node
        }
    }
    convolvers[url] = node
}

let mindspace_functions = {
    convolver: obj => {
        let [sound, volume] = obj.args
        if (sound === null) {
            if (convolver !== null) {
                convolver.disconnect(convolver_mixer)
            }
        } else {
            let [path, sum] = sound
            convolver_url = `${window.location.href.split(window.location.pathname)[0]}/${path}?${sum}`
            if (convolver_url in convolvers) {
                set_convolver(convolver_url, convolvers[convolver_url], volume)
            } else {
                audio.createReverbFromUrl(convolver_url, node => {
                    set_convolver(convolver_url, node, volume)
                })
            }
        }
    },
    copy: obj => {
        let text = obj.args[0]
        let d = document.createElement("div")
        let h = document.createElement("h2")
        h.innerText = "Copy Text"
        d.appendChild(h)
        let p = document.createElement("p")
        let e = document.createElement("textarea")
        e.value = text
        e.select()
        p.appendChild(e)
        let b = document.createElement("input")
        b.type = "button"
        b.value = "Copy"
        b.focus()
        p.appendChild(b)
        d.appendChild(p)
        game.appendChild(d)
        b.onclick = () => {
            if (document.execCommand("copy")) {
                write_message(`Copied ${text}`)
            } else {
                write_special(`Failed to copy ${text}`)
            }
            game.removeChild(d)
        }
    },
    random_sound: obj => {
        let [path, sum, x, y, z, volume] = obj.args
        get_sound(path, sum).then(get_source).then(source => {
            let p = audio.createPanner()
            let g = audio.createGain()
            g.gain.value = volume
            g.connect(mixer)
            p.connect(g)
            p.setPosition(x, y, z)
            // p.maxDistance = player.max_distance
            source.connect(p)
            source.start()
        })
    },
    object_sound: obj => {
        let [id, path, sum] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            send({name: "identify", args: [id]})
        } else {
            get_sound(path, sum).then(get_source).then(source => {
                source.connect(thing.panner)
                source.start()
            })
        }
    },
    hidden_sound: (obj) => {
        let [path, sum, x, y, z, is_dry] = obj.args
        is_dry === is_dry // Just to shut up eslint.
        get_sound(path, sum).then(get_source).then(source => {
            let p = audio.getPanner()
            let g = audio.createGain()
            g.connect(mixer)
            p.connect(g)
            p.setPosition(x, y, z)
            // p.maxDistance = player.max_distance
            source.connect(p)
            source.start()
        })
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
                let e = null
                if (typeof(type) != "string") {
                    // Should be a list. If not, then there's a server bug.
                    e = document.createElement("select")
                    e.values = {}
                    for (let key in type) {
                        let [actual, text] = type[key]
                        let v = document.createElement("option")
                        if (actual == value || actual === value) {
                            v.selected = true
                        }
                        if (text === null) {
                            text= "Nothing"
                        }
                        v.value = text
                        e.values[v.value] = actual
                        v.innerText = text
                        e.appendChild(v)
                    }
                } else {
                    let empty = ""
                    if (type == "text") {
                        e = document.createElement("textarea")
                    } else {
                        e = document.createElement("input")
                        if (type == "float" || type == "int") {
                            e.type = "number"
                            let step = null
                            if (type == "int") {
                                step = "1"
                                empty = "0"
                            } else {
                                step = "0.01"
                                empty = "0.0"
                            }
                            e.step = step
                        } else if (type == "bool") {
                            e.type = "checkbox"
                            empty = false
                            e.checked = value
                        } else {
                            if (hidden) {
                                e.type = "password"
                            } else {
                                e.type = "text"
                            }
                        }
                    }
                    e.value = value || empty
                }
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
        menu_ul.title = title
        clear_element(menu_ul)
        menu_hide.focus()
        for (let item of items) {
            let [name, command, args, kwargs] = item
            let li = document.createElement("li")
            let i = null
            if (command) {
                i = document.createElement("input")
                i.tabindex = 0
                i.type = "button"
                i.role="menuitem"
                i.value = name
                i.command = command
                i.args = JSON.stringify(args)
                i.kwargs = JSON.stringify(kwargs)
                i.onclick = menu_button
            } else {
                i = document.createElement("h3")
                i.innerText = name
            }
            li.appendChild(i)
            menu_ul.appendChild(li)
        }
    },
    remember_quit: () => {
        quitting = true
    },
    message: obj => {write_message(obj.args[0])},
    delete: obj => {
        let id = obj.args[0]
        if (objects[id] !== undefined) {
            objects[id].panner.disconnect()
            delete objects[id]
        }
    },
    identify: obj => {
        let [id, x, y, z, ambience_sound, ambience_volume] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            thing = {ambience: null, panner: audio.createPanner()}
            create_main_mixer()
            thing.panner.panningModel = "HRTF"
            thing.panner.distanceModel = "linear"
            thing.panner.connect(mixer)
            // thing.panner.maxDistance.value = player.max_distance
            objects[id] = thing
        }
        if (id == character_id) {
            // Set player perspective.
            audio.listener.setPosition(x, y, z)
        }
        thing.panner.setPosition(x, y, z)
        thing.ambience = create_ambience(thing.ambience, ambience_sound, ambience_volume, thing.panner)
    },
    interface_sound: obj => {
        let [path, sum] = obj.args
        play_sound(path, sum)
    },
    character_id: obj => {
        character_id = obj.args[0]
        let char = objects[character_id]
        audio.listener.setPosition(char.panner.positionX.value, char.panner.positionY.value, char.panner.positionZ.value)
    },
    zone: obj => {
        let [ambience_sound, ambience_rate, ambience_volume] = obj.args
        zone = create_ambience(zone, ambience_sound, ambience_volume, ambience_mixer)
        if (zone !== null && zone.source !== undefined) {
            zone.source.playbackRate.value = ambience_rate
        }
    },
    location: obj => {
        let [name, ambience_sound, ambience_volume, music_sound, max_distance] = obj.args
        player.max_distance = max_distance
        /*
        for (let id in objects) {
            objects[id].panner.maxDistance = max_distance
        }
        */
        room = create_ambience(room, ambience_sound, ambience_volume, ambience_mixer)
        music = create_ambience(music, music_sound, player.music_volume)
        if (room !== null) {
            room.name = name
        }
    },
    options: obj => {
        let [username, transmition_id, recording_threshold, sound_volume, ambience_volume, music_volume] = obj.args
        set_title(username)
        player.name = username
        player.transmition_id = transmition_id
        player.recording_threshold = recording_threshold
        player.sound_volume = sound_volume
        if (environment !== null) {
            environment.gain.value = sound_volume
        }
        player.ambience_volume = ambience_volume
        if (ambience_mixer !== null) {
            ambience_mixer.gain.value = ambience_volume
        }
        player.music_volume = music_volume
        if (music !== null && music.mixer !== undefined) {
            music.mixer.gain.value = music_volume
        }
    },
    mute_mic: () => {}
}

set_title()

connect_form.onsubmit = (e) => {
    e.preventDefault()
    let obj = {port: 6464}
    let ok = true
    for (let name of field_names) {
        let field = document.getElementById(name)
        if (!field.value) {
            alert(`You must specify a ${name.replace("_", " ")}.`)
            field.focus()
            ok = false
            break
        } else {
            Cookies.set(name, field.value, {expires: 30})
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
    soc = new WebSocket(`ws://${window.location.hostname}:6465`)
    soc.onclose = (e) => {
        if (audio !== null) {
            audio.close()
            audio = null
        }
        mixer = null
        room = null
        ambience_mixer = null
        zone = null
        music = null
        environment = null
        convolver = null
        convolver_url = null
        convolvers = {}
        sounds = {}
        objects = {}
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
        reverbjs.extend(audio)
        audio.listener.setOrientation(0, 1, 0, 0, 0, 1)
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
