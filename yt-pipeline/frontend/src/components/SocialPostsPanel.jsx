import { useState } from 'react'

const TABS = [
  { key: 'linkedin_short', label: 'LinkedIn Short' },
  { key: 'linkedin_long',  label: 'LinkedIn Long' },
  { key: 'twitter_post',   label: 'Twitter Post' },
  { key: 'twitter_thread', label: 'Twitter Thread' },
]

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    const str = Array.isArray(text) ? text.join('\n\n') : text
    navigator.clipboard.writeText(str).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <button
      onClick={handleCopy}
      className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg transition-colors"
    >
      {copied ? 'Copied!' : 'Copy to Clipboard'}
    </button>
  )
}

export function SocialPostsPanel({ linkedinShort, linkedinLong, twitterPost, twitterThread }) {
  const [activeTab, setActiveTab] = useState('linkedin_short')

  const content = {
    linkedin_short: linkedinShort,
    linkedin_long:  linkedinLong,
    twitter_post:   twitterPost,
    twitter_thread: twitterThread,
  }

  const current = content[activeTab]

  function renderContent() {
    if (activeTab === 'twitter_thread' && Array.isArray(current)) {
      return (
        <div className="space-y-3">
          {current.map((tweet, idx) => (
            <div key={idx} className="bg-gray-950 border border-gray-700 rounded-lg p-4">
              <span className="text-xs text-gray-500 font-mono mb-2 block">{idx + 1}.</span>
              <p className="text-white text-sm whitespace-pre-wrap leading-relaxed">{tweet}</p>
            </div>
          ))}
        </div>
      )
    }

    return (
      <div className="bg-gray-950 rounded-lg p-4 border border-gray-700">
        <p className="text-white text-sm whitespace-pre-wrap leading-relaxed">{current}</p>
        {activeTab === 'twitter_post' && typeof current === 'string' && (
          <p className={`text-xs mt-3 text-right ${current.length > 280 ? 'text-red-400' : 'text-gray-500'}`}>
            {current.length} / 280
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Tab bar */}
      <div className="flex border-b border-gray-800 gap-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={[
              'px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px',
              activeTab === tab.key
                ? 'text-white border-blue-500'
                : 'text-gray-500 border-transparent hover:text-gray-300',
            ].join(' ')}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {current ? (
        <div className="space-y-3">
          {renderContent()}
          <div className="flex justify-end">
            <CopyButton text={current} />
          </div>
        </div>
      ) : (
        <p className="text-gray-500 text-sm py-4 text-center">No content available.</p>
      )}
    </div>
  )
}
