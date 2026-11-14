-- Ejecutar con: osascript este_archivo.applescript /ruta/raiz/psets
-- Abre solo el pitch generado. PDF de revisión en tmp/, no entregable adicional.
on run argv
    set rootPath to item 1 of argv
    set inputPath to rootPath & "/pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.pptx"
    set pdfPath to rootPath & "/tmp/pitch-revision.pdf"
    set pptPath to rootPath & "/pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.ppt"
    tell application "Microsoft PowerPoint"
        open POSIX file inputPath
        set deck to active presentation
        set slideCount to count of slides of deck
        if slideCount is not 6 then error "La presentación no tiene seis diapositivas"
        save deck in POSIX file pdfPath as save as PDF
        save deck in POSIX file pptPath as save as presentation
        close deck saving no
        open POSIX file pptPath
        set legacyDeck to active presentation
        if (count of slides of legacyDeck) is not 6 then error "El PPT convertido no tiene seis diapositivas"
        save legacyDeck in POSIX file (rootPath & "/tmp/ppt-revision.pdf") as save as PDF
        close legacyDeck saving no
        return "Conversión completada: " & slideCount & " diapositivas"
    end tell
end run
