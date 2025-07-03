import Image from "next/image";

import GirlRaising from "@/../public/girl-raising.png";
import LoginPage from "@/components/pages/login";

export default function Login() {
  return (
    <div className="w-screen h-screen bg-gray-170 flex">
      <div className="w-4/7 h-full flex justify-center items-center">
        <Image src={GirlRaising} width={550} height={300} alt="Girl raising" />
      </div>
      <div className="w-3/7 h-screen items-center justify-center">
        <h1 className="typing">Learnify</h1>
        <LoginPage />
      </div>
    </div>
  );
}
