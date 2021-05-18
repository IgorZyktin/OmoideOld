function goSearch(form) {
    // rewrite + symbol in query into %2B and update parameters
    let element = document.getElementById("query_element");
    element.value = element.value.replaceAll("\+", "%2B")
    element.value = element.value.replaceAll(/\s+/g, " ")

    let searchParams = new URLSearchParams(window.location.search);
    form.action = "/search?" + searchParams.toString();
}

function toggleTheme(theme_uuid) {
    // include or exclude theme from search
    let element = document.getElementById('toggle_' + theme_uuid)
    let theme = document.getElementById('theme_' + theme_uuid)

    if (!element) {
        console.log('Could not find toggle element toggle_' + theme_uuid)
        return
    }

    if (!theme) {
        console.log('Failed to get theme element theme_' + theme_uuid)
        return
    }

    visibility[theme_uuid] = !visibility[theme_uuid]

    if (visibility[theme_uuid]) {
        theme.classList.add('nav-chosen-theme')
        element.checked = false
    } else {
        theme.classList.remove('nav-chosen-theme')
        element.checked = true
    }
    applyFiltering()
}

function switchThemeFolding(theme_uuid) {
    // show or hide list of groups for this theme
    let image = document.getElementById('fold_' + theme_uuid)
    let element = document.getElementById('groups_' + theme_uuid)

    if (!element) {
        // theme can have no groups
        return
    }

    if (element.style.display === 'none' || !element.style.display) {
        image.src = "../static/collapse-arrow.svg";
        element.style.display = 'block'
    } else {
        image.src = "../static/expand-arrow.svg";
        element.style.display = 'none'
    }
}

function applyFiltering() {
    // alter active_themes parameter
    let searchParams = new URLSearchParams(window.location.search);
    let keys = Object.keys(visibility).filter(k => visibility[k])

    if (keys.length === 0) {
        searchParams.set("active_themes", "no_themes");
    } else if (keys.length === Object.keys(visibility).length) {
        searchParams.set("active_themes", "all_themes");
    } else {
        searchParams.set("active_themes", keys.join('%2C'));
    }

    let newUrl = "/navigation?" + searchParams.toString();
    window.history.pushState({path: newUrl}, '', newUrl);

    let tagsButton = document.getElementById('tagsButton')
    tagsButton.href = "/tags?" + searchParams.toString();
}

function toggleAllThemes(checked) {
    // set all themes as active/inactive
    Object.keys(visibility).forEach(v => visibility[v] = checked)
    updateAllThemes()
    applyFiltering()
}

function updateAllThemes() {
    // sync visible theme states with visibility map
    for (const [theme_uuid, isVisible] of Object.entries(visibility)) {
        let element = document.getElementById('toggle_' + theme_uuid)
        let theme = document.getElementById('theme_' + theme_uuid)

        if (!element) {
            console.log('Could not find toggle element toggle_' + theme_uuid)
            continue
        }

        if (!theme) {
            console.log('Could not find theme element theme_' + theme_uuid)
            continue
        }

        if (isVisible) {
            theme.classList.add('nav-chosen-theme')
            element.checked = true
        } else {
            theme.classList.remove('nav-chosen-theme')
            element.checked = false
        }
    }
}

function explainSearchResults() {
    // toggle explanation block
    let element = document.getElementById('explain')

    if (!element)
        return

    if (element.style.display === 'none' || !element.style.display) {
        element.style.display = 'grid'
    } else {
        element.style.display = 'none'
    }
}

// function copy(text) {
//     // copy given text to buffer
//     let input = document.createElement('input');
//     input.setAttribute('value', text);
//     document.body.appendChild(input);
//     input.select();
//     let result = document.execCommand('copy');
//     document.body.removeChild(input);
//     return result;
// }
