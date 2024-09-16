export default function Footer(){
    return <>
        <footer className="w-full flex justify-center shadow-[inset_0_-2px_0_rgba(20,20,20,1)]">
            <div className="w-[1280px] flex justify-start items-center">
                <p className="py-8 text-muted-foreground">
                    Built by <a href="https://github.com/Nenad005" target="_blank" className="underline-offset-4 underline cursor-pointer">Nenad005</a>
                    . The source code is available on <a href="https://github.com/Nenad005/google-maps-scraper" target="_blank" className="underline-offset-4 underline cursor-pointer">GitHub</a>.
                </p>
            </div>
        </footer>
    </>
}