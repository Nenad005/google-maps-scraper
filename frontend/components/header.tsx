import Image from "next/image"
import logo from '../res/unnamed.png'
import { Separator } from "@radix-ui/react-select"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"

export default function Header(){
    return <>
        <header className="w-full flex bg-background justify-center shadow-[inset_0_-2px_0_var(--border)]">
            <nav className="w-[1280px] flex justify-start items-end py-8 gap-x-5">
                <a className="flex justify-center items-end gap-5">
                    <Image src={logo} alt="logo image" className="w-10 h-10"></Image>
                    <h1 className="font-bold text-4xl">GM <span className="tracking-widest">Leads</span></h1>
                </a>
                <h1 className="">Leads</h1>
                <h1>Statistics</h1>
                <a className="flex ml-auto justify-center items-end gap-5">
                    <h1 className="font-thin text-4xl">Nenad005</h1>
                    <Avatar >
                        <AvatarImage src="https://github.com/Nenad005.png" />
                    </Avatar>
                </a>
            </nav>
        </header>
        <Separator className=""></Separator>
    </>
}