export default function Home() {
    return (
        <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-900 mb-4">
                    CirclePortal
                </h1>
                <p className="text-xl text-gray-600 mb-8">
                    東京工科大学サークル情報ポータル
                </p>
                <div className="flex gap-4 justify-center">
                    <a
                        href="/circles?campus=hachioji"
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        八王子キャンパス
                    </a>
                    <a
                        href="/circles?campus=kamata"
                        className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                    >
                        蒲田キャンパス
                    </a>
                </div>
                <div className="mt-12 text-sm text-gray-500">
                    Setup completed ✓
                </div>
            </div>
        </main>
    );
}
