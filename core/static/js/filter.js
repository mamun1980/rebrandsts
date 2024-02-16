const filterList = (val, name) => {
    console.log(val);
    console.log(name);

    const url = new URL(window.location.href);
    const searchParams = new URLSearchParams(url.search);

    if (searchParams.has(name)) {
        // Update the existing parameter
        searchParams.set(name, val);
    } else {
        // Add a new parameter
        searchParams.append(name, val);
    }

    // Create a new URL with the updated search parameters
    const newUrl = new URL(url);
    newUrl.search = searchParams.toString();
    console.log(newUrl.href);
    window.location.href = newUrl.href;
};
