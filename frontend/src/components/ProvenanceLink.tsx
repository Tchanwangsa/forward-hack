// Renders `tel:` / `eml:` / `tx:` / `wo:` / `round:` as a link into the artifact pane.
export default function ProvenanceLink({ ref: r }: { ref: string }) {
  return <code className="text-xs text-blue-700">{r}</code>
}
