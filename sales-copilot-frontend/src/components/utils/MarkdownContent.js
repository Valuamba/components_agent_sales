import { marked } from "marked";


const MarkdownContent = ({ className, markdown }) => {
    const htmlContent = marked.parse(markdown);

    return (
      <pre
        className={className}
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    );
  }


export default MarkdownContent;
