/* global Cookies, reverbjs */

let cookies_options = {expires: 365}
let recorder = null
let cancel_recording = false
let recording = "recording"
let microphone_data = null
let speech_data = null

let ArrayType = Uint8Array
// The following code was taken from
// https://developers.google.com/web/updates/2012/06/How-to-convert-ArrayBuffer-to-and-from-String
// <code>

function ab2str(buf) {
    return String.fromCharCode.apply(null, new ArrayType(buf))
}

function str2ab(str) {
    let buf = new ArrayBuffer(str.length*2) // 2 bytes for each char
    let bufView = new ArrayType(buf)
    for (let i=0, strLen=str.length; i < strLen; i++) {
        bufView[i] = str.charCodeAt(i)
    }
    return buf
}
// </code>

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
let room_ambience = null
let zone = null
let music = null

let escape_element = null

let quitting = false

function show(element) {
    escape_element = element
    element.hidden = false
}

function hide(element) {
    if (escape_element === element) {
        escape_element = null
    }
    element.hidden = true
    disconnect.focus()
}

function scroll_bottom() {
    window.scrollTo(0,document.body.scrollHeight)
}

function create_panner(max_distance) {
    let p = audio.createPanner()
    if (max_distance !== undefined) {
        p.maxDistance = max_distance
    }
    p.panningModel = "HRTF"
    p.distanceModel = "linear"
    return p
}

function create_ambience(obj, sound, volume, output, rate) {
    create_environment()
    if (rate === undefined) {
        rate = 1
    }
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
            if (obj.mixer === null || obj.mixer === undefined) {
                // Let's build us a mixer.
                obj.mixer = audio.createGain()
                obj.mixer.connect(output)
            }
            get_sound(path, sum).then(get_source).then(source => {
                obj.path = path,
                obj.sum = sum,
                obj.source = source
                source.loop = true
                source.playbackRate.value = rate
                source.connect(obj.mixer)
                source.start(0)
            })
        } else {
            obj.source.playbackRate.value = rate
        }
        obj.mixer.gain.value = volume
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
            if (environment === null) {
                create_environment()
            }
            output = environment
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
        environment = create_mixer(player.sound_volume, audio.destination)
        navigator.mediaDevices.getUserMedia({audio: true, video: false}).then(
            stream => {
                if (MediaRecorder === undefined) {
                    write_message("*** No MediaRecorder available. Recording your voice will be impossible on this device. ***")
                } else {
                    recorder = new MediaRecorder(stream)
                    recorder.ondataavailable = (e) => {
                        if (cancel_recording) {
                            return
                        }
                        let webm = new Blob(new Array(e.data), { type: "audio/m4a"})
                        let reader = new FileReader()
                        reader.onloadend = () => {
                            microphone_data = reader.result
                            send({name: "speak", args: [ab2str(microphone_data)]})
                        }
                        reader.readAsArrayBuffer(webm)
                    }
                }
            }, () => {
                alert("Failed to use microphone.")
            }
        )
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
                let url = `${window.location.href.split(window.location.pathname)[0]}/${path}?${sum}`
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

let voice_voice = document.getElementById("voice-voice")

voice_voice.onchange = () => {
    Cookies.set("voice_voice", voice_voice.value, cookies_options)
}

let tts = window.speechSynthesis
let voice_enable = document.getElementById("voice-enable")
voice_enable.checked = Cookies.get("voice_enable") == "true" ? true : false

voice_enable.onchange = () => {
    Cookies.set("voice_enable", voice_enable.checked, cookies_options)
}

let voice_rate = document.getElementById("voice-rate")
voice_rate.value = Cookies.get("voice_rate") || 1

voice_rate.onchange = () => {
    Cookies.set("voice_rate", voice_rate.value, cookies_options)
}

let map = document.getElementById("map")
map.width = map.height = Math.min(window.screen.height, window.screen.width)
// let gl = map.getContext("2d", { alpha: false })
let output = document.getElementById("output")
document.getElementById("username").focus()

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

let keyboard_transformations = {
    "¬": "`",
    "!": "1",
    "\"": "2",
    // "£": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    ")": "0",
    "_": "-",
    "+": "=",
    "{": "[",
    "}": "]",
    ":": ";",
    "@": "'",
    "~": "#",
    "<": ",",
    ">": ".",
    "?": "/",
    "|": "\\",
}

keyboard_transformations[String.fromCharCode(163)] = "3"

function standard_key(e) {
    // Send a key.
    if (!connected) {
        return
    }
    let mods = []
    for (let control of document.querySelectorAll(".key-modifier")) {
        if (control.checked) {
            mods.push(control.value)
            control.checked = false
        }
    }
    let button = e.target
    send({
        name: "key",
        args: [button.value, mods]
    })
}

for (let button of document.querySelectorAll(".key-standard")) {
    button.onclick = standard_key
}

document.ontouchstart = unlock_audio
document.onkeydown = (e) => {
    let current = document.activeElement
    if (
        (
            (
                e.key != "ESCAPE"
            ) && (
                e.key === undefined || !connected || [
                    "text", "password", "textarea", "number", "select-one"
                ].includes(current.type)
            )
        ) || (
            current.className == "url"
        )
    ) {
        return
    }
    let key = e.key.toUpperCase()
    if (escape_element === menu && e.key != "ESCAPE") {
        let func = menu_keys[key]
        if (func !== undefined) {
            func(e)
        }
        return
    }
    if (key == "CONTROL") {
        window.speechSynthesis.cancel()
    }
    let modifiers = []
    for (let name of ["ctrl", "shift", "alt"]) {
        if (e[`${name}Key`]) {
            modifiers.push(name)
        }
    }
    if (keyboard_transformations[key] !== undefined) {
        key = keyboard_transformations[key]
    }
    if (!modifiers.count && key == "ESCAPE" && escape_element !== null) {
        hide(escape_element)
    } else if (escape_element === copy_div && current.type == "button" && !modifiers.count && [" ", "ENTER"].includes(key)) {
        return
    } else {
        if (["'", "ENTER", " ", "TAB", "W", "Q", "T", "N"].includes(key) || key[0] == "F") {
            e.preventDefault()
        }
        send({name: "key", args: [key, modifiers]})
    }
}

let copy_div = document.getElementById("copy")
let copy_text = document.getElementById("copy-text")
let copy_button = document.getElementById("copy-button")
copy_button.onclick = () => {
    let text = copy_text.value
    if (document.execCommand("copy")) {
        write_message(`Copied ${text}`)
    } else {
        write_special(`Failed to copy ${text}`)
    }
    hide(copy_div)
}

let connect_form = document.getElementById("connect-form")
let connect = document.getElementById("connect")

let game = document.getElementById("game")

let menu = document.getElementById("menu")
let menu_h = document.getElementById("menu-h")
let menu_ul = document.getElementById("menu-ul")
let menu_index = null
let menu_search = ""
let menu_last_search = 0
let menu_search_interval = 1000 // Milliseconds
let menu_hide = document.getElementById("menu-hide")
menu_hide.onclick = () => {
    hide(menu)
}

let menu_keys = {
    "ARROWDOWN": () => {
        if (menu_index === null) {
            menu_index = 0
        }
        menu_index = Math.min(menu_ul.children.length - 1, menu_index + 1)
        menu_ul.children[menu_index].firstChild.focus()
    },
    "ARROWUP": () => {
        menu_index = Math.max(0, menu_index - 1)
        menu_ul.children[menu_index].firstChild.focus()
    },
    HOME: () => {
        menu_index = -1
        menu_keys.ARROWDOWN()
    },
    END: () => {
        menu_index = menu_ul.children.length
        menu_keys.ARROWUP()
    },
    "ENTER": () => true
}

function search_menu(e) {
    let now = new Date().getTime()
    if (now - menu_last_search >= menu_search_interval) {
        menu_search = ""
        menu_index = 0
    }
    menu_last_search = now
    menu_search += e.key.toLowerCase()
    for (let i = menu_index; i < menu_ul.children.length; i++) {
        let child = menu_ul.children[i]
        let button = child.firstChild
        if (button.value !== undefined && button.value.toLowerCase().startsWith(menu_search)) {
            button.focus()
            menu_index = i
            return false
        }
    }
}

for (let char of "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 -='#/\\`[],.") {
    menu_keys[char] = search_menu
}

let text = document.getElementById("text")

let text_cancel = document.getElementById("text-cancel")
text_cancel.onclick = () => {
    hide(text)
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
    hide(text)
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
    hide(form)
}

let form_h = document.getElementById("form-h")
let form_p = document.getElementById("form-p")
let form_hide = document.getElementById("form-hide")
form_hide.onclick = () => {
    hide(form)
}
let form_ok = document.getElementById("form-ok")

let form_command = {
    name: null,
    args: [],
    kwargs: {}
}
let form_fields = {}

hide_elements()

let disconnect = document.getElementById("disconnect")
disconnect.onclick = () => {
    if (connected) {
        send({name: "quit"})
    } else {
        alert("You are not connected.")
    }
}

function menu_button(e) {
    escape_element = null
    let i = e.target
    hide(menu)
    send(
        {
            name: i.command,
            args: JSON.parse(i.args),
            kwargs: JSON.parse(i.kwargs)
        }
    )
}

function clear_element(e) {
    // Below code based on the first answer at:
    // https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
    while (e.firstChild) {
        e.removeChild(e.firstChild)
    }
}

function hide_elements() {
    for (let element of document.getElementsByClassName("mindspace-hidden")) {
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
    if (voice_enable.checked) {
        let msg = new SpeechSynthesisUtterance(text)
        msg.rate = parseInt(voice_rate.value)
        let voice_index = parseInt(voice_voice.value)
        if (voice_index != -1) {
            msg.voice = tts.getVoices()[voice_index]
        }
        tts.speak(msg)
    }
    let p = document.createElement("p")
    p.innerText = text
    output.appendChild(p)
    scroll_bottom()
    return p
}

function write_special(text) {
    write_message(`--- ${text} ---`)
}

// All the objects the client knows about:
let objects = {}

// The current player object:
let player = {
    name: null,
    sound_volume: null,
    ambience_volume: null,
    music_volume: null,
}

function set_convolver(url, node, volume) {
    if (convolver_mixer === null) {
        convolver_mixer = audio.createGain()
        convolver_mixer.connect(environment)
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
    toggle_recording: () => {
        if (recorder === null || recorder.state == recording) {
            mindspace_functions.stop_recording()
        } else {
            mindspace_functions.start_recording()
        }
    },
    start_recording: () => {
        cancel_recording = false
        recorder.start()
    },
    stop_recording: () => {
        if (recorder === null) {
            write_message("You cannot record audio on this device.")
        } else {
            recorder.stop()
        }
    },
    cancel_recording: () => {
        cancel_recording = true
        mindspace_functions.stop_recording()
    },
    convolver: obj => {
        let [sound, volume] = obj.args
        if (sound === null) {
            if (convolver !== null) {
                try {
                    convolver.disconnect(convolver_mixer)
                }
                catch (err) {
                    // In case someone messed up the convolver with a text file for example.
                }
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
        show(copy_div)
        copy_text.value = text
        copy_text.select()
        copy_button.focus()
    },
    random_sound: obj => {
        let [path, sum, x, y, z, volume, max_distance] = obj.args
        get_sound(path, sum).then(get_source).then(source => {
            let p = create_panner(max_distance)
            let g = audio.createGain()
            g.connect(mixer)
            p.connect(g)
            g.gain.value = volume
            p.setPosition(x, y, z)
            source.connect(p)
            source.start()
        })
    },
    speak: obj => {
        let [id, data] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            send({name: "identify", args: [id]})
        } else {
            speech_data = data
            let array = str2ab(speech_data)
            let result = audio.decodeAudioData(array).then((buffer) => {
                let source = audio.createBufferSource()
                source.connect(thing.panner)
                source.buffer = buffer
                source.start()
            }, (e) => {
                write_message(`Someone spoke but your device was unable to decode the audio data: ${e.err}`)
            })
            if (result === null) {
                write_message("Someone spoke but your device was unable to decode the audio data.")
            }
        }
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
        let [path, sum, x, y, z, is_dry, volume, max_distance] = obj.args
        get_sound(path, sum).then(get_source).then(source => {
            let p = create_panner(max_distance)
            let g = audio.createGain()
            if (is_dry) {
                g.connect(environment)
            } else {
                g.connect(mixer)
            }
            g.gain.value = volume
            p.connect(g)
            p.setPosition(x, y, z)
            source.connect(p)
            source.start()
        })
    },
    url: obj => {
        let [title, href] = obj.args
        let a = document.createElement("a")
        a.target = "_blank"
        a.className = "url"
        a.href = href
        a.innerText = title
        output.appendChild(a)
        a.focus()
        a.onclick = () => {
            disconnect.focus()
        }
    },
    get_text: obj => {
        let [message, command, value, multiline, escapable, args, kwargs] = obj.args
        show(text)
        if (!escapable) {
            escape_element = null
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
        e.onkeyup = (evt) => {
            if (evt.key == "Escape" && escape_element !== null) {
                hide(escape_element)
            }
        }
        text_element = e
        clear_element(text_field)
        text_field.appendChild(e)
        e.select()
        e.focus()
    },
    form: obj => {
        let [title, fields, command, args, kwargs, ok, cancel] = obj.args
        show(form)
        form_h.innerText = title
        form_ok.innerText = ok
        if (cancel !== null) {
            form_hide.innerText = cancel
        }
        form_hide.focus()
        clear_element(form_p)
        form_command = {
            name: command,
            args: args,
            kwargs: kwargs
        }
        form_fields = {}
        for (let index in fields) {
            let data = fields[index]
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
                let id = `form-field-${index}`
                e.setAttribute("id", id)
                i = document.createElement("p")
                i.style.width = "100%"
                let l = document.createElement("label")
                l.style.width = "10%"
                l.setAttribute("for", id)
                l.innerText = `${title} `
                i.appendChild(l)
                e.style.width = "90%"
                i.appendChild(e)
                form_fields[name] = e
            }
            form_p.appendChild(i)
        }
    },
    menu: obj => {
        let [title, items, escapable] = obj.args
        menu_index = null
        menu_search = ""
        menu_last_search = 0
        show(menu)
        if (!escapable) {
            escape_element = null
        }
        menu_h.innerText = title
        menu_ul.title = title
        clear_element(menu_ul)
        menu_hide.focus()
        for (let item of items) {
            let [name, command, args, kwargs] = item
            let li = document.createElement("li")
            let i = document.createElement("input")
            i.type = "button"
            i.role="menuitem"
            if (command) {
                i.command = command
                i.args = JSON.stringify(args)
                i.kwargs = JSON.stringify(kwargs)
                i.onclick = menu_button
            } else {
                name = `- ${name} -`
            }
            i.value = name
            li.appendChild(i)
            menu_ul.appendChild(li)
        }
    },
    remember_quit: () => {
        quitting = true
    },
    message: obj => {
        let message = obj.args[0]
        let style = obj.args[2]
        let p = write_message(message)
        if (style !== null) {
            p.style.cssText = style
        }
    },
    delete: obj => {
        let id = obj.args[0]
        if (objects[id] !== undefined) {
            objects[id].panner.disconnect()
            delete objects[id]
        }
    },
    identify: obj => {
        let [id, x, y, z, ambience_sound, ambience_volume, max_distance] = obj.args
        let thing = objects[id]
        if (thing === undefined) {
            thing = {ambience: null, panner: create_panner()}
            create_main_mixer()
            thing.panner.connect(mixer)
            objects[id] = thing
        }
        thing.panner.maxDistance = max_distance
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
        if (char !== undefined) {
            audio.listener.setPosition(char.panner.positionX.value, char.panner.positionY.value, char.panner.positionZ.value)
        } else {
            send({name: "identify", args: [character_id]})
        }
    },
    zone: obj => {
        let [ambience_sound, ambience_rate, ambience_volume] = obj.args
        zone = create_ambience(zone, ambience_sound, ambience_volume, ambience_mixer, ambience_rate)
    },
    location: obj => {
        let [name, ambience_sound, ambience_volume, music_sound] = obj.args
        room_ambience = ambience_sound
        let r = create_ambience(room, ambience_sound, ambience_volume, ambience_mixer)
        if (room_ambience == ambience_sound) {
            room = r
        }
        music = create_ambience(music, music_sound, player.music_volume)
        if (room !== null) {
            room.name = name
        }
    },
    options: obj => {
        let [username, sound_volume, ambience_volume, music_volume] = obj.args
        set_title(username)
        player.name = username
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
            obj[name] = field.value
        }
    }
    if (ok) {
        create_socket(obj)
    }
    return false
}

function create_socket(obj) {
    clear_element(voice_voice)
    let o = document.createElement("option")
    o.value = -1
    o.selected = true
    o.innerText = "Default"
    voice_voice.appendChild(o)
    for (let i in tts.getVoices()) {
        let voice = tts.getVoices()[i]
        let o = document.createElement("option")
        o.value = i
        o.innerText = `${voice.name} (${voice.lang})`
        voice_voice.appendChild(o)
    }
    voice_voice.value = Cookies.get("voice_voice") || -1
    hide(connect)
    game.hidden = false
    if (window.WebSocket === undefined) {
        write_message("Your browser doesn't support this client. Please use a browser like FIrefox or Chrome.")
    } else {
        soc = new window.WebSocket(`wss://${window.location.hostname}:6465`)
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
            convolver_mixer = null
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
            if (AudioContext) {
                audio = new AudioContext()
                reverbjs.extend(audio)
                audio.listener.setOrientation(0, 1, 0, 0, 0, 1)
            } else {
                alert("Your web browser does not support audio.")
            }
            write_special("Connection Open")
            clear_element(output)
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
}
