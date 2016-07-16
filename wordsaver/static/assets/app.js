(function(global) {
    /* template loader */
    function getTemplate(name, url) {
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest()
            xhr.open("get", url)
            xhr.onload = (e) => {
                resolve({ name, "value": xhr.responseText })
            }
            xhr.onerror = (e) => {
                reject(e)
            }
            xhr.send()
        })
    }

    function getTemplates(templs) {
        return Promise.all(
            templs.map(
                ({name, url}) => getTemplate.call(void 0, name, url)
            )
        )
    }

    getTemplates([
        { "name": "wordItemTemplate", "url": "wordItem.html" },
        { "name": "modalTemplate", "url": "modal.html" },
        { "name": "toastTemplate", "url": "toast.html" }
    ]).then((tmpls) => {
        setup(tmpls.reduce((acc, {name, value}, idx) => { acc[name] = value; return acc }, Object.create(null)))
    })

    /* audio player */
    class AudioPlayer {
        constructor() {
            this.cache = new Map()
        }

        play(src) {
            var a = this.cache.get(src)
            if (!a) {
                a = new Audio(src)
                this.cache.set(src, a)
            }
            a.play()
        }
    }

    var audioPlayer = new AudioPlayer()

    function setup(templates) {
        /* extensions */
        Vue.use(VueResource)

        /* components */
        Vue.component("wordItem", {
            props: ["word"],
            template: templates["wordItemTemplate"],
            methods: {
                querybing(wid) {
                    wordresource.get({wid, refresh: "yes"})
                    .then((res) => {
                        this.$set("word", res.json().result)
                    }, (err) => {
                        this.$dispatch("toast-msg", "error", "必应查词失败")
                    })
                }
            }
        })

        Vue.component("modalBox", {
            "props": ["show"],
            "template": templates["modalTemplate"]
        })

        Vue.component("toast", {
            props: {
                messages: { required: true }
            },
            template: templates["toastTemplate"]
        })

        /* App */
        var wordresource = Vue.resource("/word{/wid}")
        var app = new Vue({
            el: "#app",
            data: {
                "query": "",
                "show": false,
                "rawwords": [],
                "word": void 0,
                "messages": [ ]
            },
            computed: {
                words() {
                    if(this.query) {
                        re = new RegExp(this.query)
                        if (re) {
                            return this.rawwords.filter(
                                ({wid, word}) => re.test(word))
                        } else {
                            return this.rawwords.filter(
                                ({wid, word}) => word.indexOf(this.query) != -1
                            )
                        }
                    }
                    return this.rawwords
                }
            },
            methods: {
                refresh() {
                    wordresource.get()
                    .then((res) => {
                        this.$set("rawwords", res.json().result)
                    }, err => this.$dispatch("toast-msg", "error", `Failed to fetch word list.\n${toErrMsg(err)}`))
                },
                showWord(wid) {
                    wid = parseInt(wid)
                    if (wid) {
                        wordresource.get({wid})
                        .then(res => {
                            this.word = res.json().result
                            this.show = true
                        }, err => this.$dispatch("toast-msg", "error", "Failed to fetch word info."))
                    }
                },
                removeWord(wid) {
                    wid = parseInt(wid)
                    if(wid) {
                       wordresource.remove({wid})
                       .then((res) => this.refresh() || this.$dispatch("toast-msg", "info", "单词已删除。")
                            , (err) => this.$dispatch("toast-msg", "error", toErrMsg(err)))
                    }
                },
                addword(word) {
                    if (word && typeof word === "string") {
                        wordresource.save({word})
                        .then((res) => {
                            this.query = ""
                            this.refresh()
                        }, (err) => this.$dispatch("toast-msg", "error", toErrMsg(err)))
                    }
                }
            },
            events: {
                "toast-msg"(type, text) {
                    this.messages.push({type, text})
                    setTimeout(() => this.messages.shift(), 3000);
                },
                "audio-play"(src) {
                    audioPlayer.play(src)
                }
            },
            ready() {
                this.refresh()
            }
        })

        function toErrMsg(err) {
            var json
            if(json = err.json()) {
                return json.message || json.msg || JSON.stringify(json)
            } else {
                return err.data
            }
        }
    }
})(this)
