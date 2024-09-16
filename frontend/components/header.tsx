export default function Header(){
    return <>
        <header className="h-16 w-full flex justify-center shadow-[inset_0_-2px_0_rgba(20,20,20,1)]">
            <nav className="w-[1280px] h-full flex justify-start items-center">
                <a className="flex">
                    <h1>LOGO</h1>
                    <h1>GM Leads</h1>
                </a>
                <h1>Leads</h1>
                <h1>Statistics</h1>
                <a className="flex ml-auto">
                    <h1>Username</h1>
                    <h1>PFP</h1>
                </a>
            </nav>
        </header>
    </>
}