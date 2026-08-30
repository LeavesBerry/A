import { watch } from "vue"

const timers = {}

function getStorage(type = "local") {
    return type === "session" ? sessionStorage : localStorage
}

function save(storage, key, value) {
    storage.setItem(key, JSON.stringify(value))
}

function saveDelay(storage, key, value, delay) {
    clearTimeout(timers[key])
    timers[key] = setTimeout(() => {
        save(storage, key, value)
        delete timers[key]
    }, delay)
}

export function restorePersist(state, config) {
    for (const [field, option] of Object.entries(config)) {
        const storage = getStorage(option.storage)
        const key = option.key ?? field
        const rawValue = storage.getItem(key)
        if (rawValue === null) continue
        try {
            state[field] = JSON.parse(rawValue)
        } catch (error) {
            console.warn(`[persist] 恢复字段 "${field}" 失败`, error)
            storage.removeItem(key)
        }
    }
}

export function setupPersist(state, config) {
    for (const [field, option] of Object.entries(config)) {
        if (option.type === "rare") continue
        const storage = getStorage(option.storage)
        const key = option.key ?? field
        if (option.type === "frequent") {
            watch(
                () => state[field],
                value => save(storage, key, value),
                { deep: option.deep ?? false }
            )
            continue
        }
        if (option.type === "burst") {
            watch(
                () => state[field],
                value => saveDelay(
                    storage,
                    key,
                    value,
                    option.delay ?? 1000
                ),
                { deep: option.deep ?? false }
            )
        }
    }
}

export function updatePersistFields(state, values, config) {
    const result = {
        updated: [],
        skipped: []
    }
    for (const [field, value] of Object.entries(values)) {
        const option = config[field]
        if (!option) {
            console.warn(`[persist] 字段 "${field}" 没有持久化配置`)
            result.skipped.push(field)
            continue
        }
        state[field] = value
        if (option.type !== "rare") {
            result.updated.push(field)
            continue
        }
        try {
            const storage = getStorage(option.storage)
            save(storage, option.key ?? field, value)
            result.updated.push(field)
        } catch (error) {
            console.error(`[persist] 保存字段 "${field}" 失败`, error)
            result.skipped.push(field)
        }
    }
    return result
}

export function removePersistFields(fields, config) {
    const fieldList = Array.isArray(fields) ? fields : [fields]
    for (const field of fieldList) {
        const option = config[field]
        if (!option) continue
        const key = option.key ?? field
        const storage = getStorage(option.storage)
        storage.removeItem(key)
        clearTimeout(timers[key])
        delete timers[key]
    }
}

export const persistConfig = {
    isLogined: {
        type: "rare",
        storage: "local"
    },
    userName: {
        type: "rare",
        storage: "local"
    },
    userId: {
        type: "rare",
        storage: "local"
    },
    userEmail: {
        type: "rare",
        storage: "local"
    },
    bio: {
        type: "rare",
        storage: "local"
    },
    userAccessToken: {
        type: "rare",
        storage: "local"
    },
    avatarUrl: {
        type: "rare",
        storage: "local"
    },
    level: {
        type: "rare",
        storage: "local"
    },
    xp: {
        type: "burst",
        storage: "local",
        delay: 500
    }
}
