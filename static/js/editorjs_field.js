$(function () {
  const jsonOutputElementId = document.getElementById('codex-editor').getAttribute('output-id');
  const jsonOutputElement = document.getElementById(jsonOutputElementId);
  let initialContent = undefined;
  try {
    initialContent = JSON.parse(jsonOutputElement.value);
  } catch (e) {
  }
  const editor = new EditorJS({
    holder: 'codex-editor',
    onChange: () => {
      editor.save().then(result => {
        jsonOutputElement.value = encodeURI(JSON.stringify(result, null, 0));
      });
    },
    tools: {

      header: {
        class: Header,
        inlineToolbar: ['link'],
        config: {
          placeholder: 'Header'
        },
      },
      image: {
        class: SimpleImage,
        inlineToolbar: ['link'],
      },
      // list: {
      //   class: List,
      //   inlineToolbar: true,
      // },
      quote: {
        class: Quote,
        inlineToolbar: true,
        config: {
          quotePlaceholder: 'Enter a quote',
          captionPlaceholder: 'Quote\'s author',
        },
      },
      marker: Marker,
      //code:  CodeTool,
      delimiter: Delimiter,
      inlineCode: InlineCode,
      // linkTool: LinkTool,
      embed: Embed,
      table: {
        class: Table,
        inlineToolbar: true,
      },
    },
    data: initialContent || {}
  });
});
