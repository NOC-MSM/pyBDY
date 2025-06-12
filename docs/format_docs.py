import glob

markdown_files = glob.glob("./*.md")
index_files = glob.glob("./index*.md")

markdown_mods = list(set(markdown_files) - set(index_files))

for i in range(len(markdown_mods)):
    with open(markdown_mods[i], "r") as f:
        data = f.readlines()

    skip_ind = []
    for j in range(len(data)):
        # Swap args for parameters and remove colons
        if "Arg" in data[j]:
            data[j] = data[j].replace("s", "").replace("Arg", "Parameters")
        if (
            ("Parameters" in data[j]) | ("Returns" in data[j]) | ("Notes" in data[j])
        ) & (":" in data[j]):
            data[j] = data[j].replace(":", "")

        # Upgrade some headings
        if ("# " in data[j]) & ("package" not in data[j]) & ("##" not in data[j]):
            data[j] = data[j].replace("# ", "")
        if (" module" in data[j]) & ("## " in data[j]):
            data[j] = data[j].replace("## ", "# ")
        if (
            ("### " in data[j])
            & ("Parameters" not in data[j])
            & ("Returns" not in data[j])
            & ("Notes" not in data[j])
        ):
            data[j] = data[j].replace("### ", "## ")
        data[j] = data[j].replace("#### ", "### ")
        if ("Parameters" in data[j]) | ("Returns" in data[j]):
            data[j] = "> " + data[j]
        if (
            ("### " in data[j])
            & ("Parameters" not in data[j])
            & ("Returns" not in data[j])
            & ("Notes" not in data[j])
        ):
            data[j] = data[j].replace("### ", "### *method* ")

        # Remove notes headings
        if "## Notes" in data[j]:
            skip_ind.append(j)

        # Indent arguments
        if (":" in data[j]) & (data[j][0] != ">"):
            data[j] = "> " + data[j]
        if data[j][0] == ">":
            data[j] = data[j][:-1] + "<br>" + data[j][-1]

    with open(markdown_mods[i], "w") as f:
        for j in range(len(data)):
            if len(skip_ind) > 0:
                if j in skip_ind:
                    continue
            f.write(data[j])
