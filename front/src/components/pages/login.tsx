"use client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
export default function LoginPage() {
  const login = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Handle form submission logic here
    return (
      <Alert>
        <AlertTitle>Success! Your changes have been saved</AlertTitle>
        <AlertDescription>
          This is an alert with icon, title and description.
        </AlertDescription>
      </Alert>
    );
  };

  return (
    <form
      className="flex w-[35rem] h-[30rem] rounded-xl forms-bg justify-center items-center max-w-md "
      onSubmit={login}
    >
      <div className="flex w-96 flex-col gap-6 bg-transparent shadow-2xl">
        <Tabs defaultValue="Login">
          <TabsList>
            <TabsTrigger value="Login">Login</TabsTrigger>
            <TabsTrigger value="Register">Cadastre-se</TabsTrigger>
          </TabsList>
          <TabsContent value="Login">
            <Card>
              <CardHeader>
                <CardTitle>Login</CardTitle>
                <CardDescription>
                  Entre e desfrute dos seus cursos favoritos.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="tabs-demo-name">Usuário</Label>
                  <Input
                    id="tabs-demo-name"
                    placeholder="Coloque seu usuário aqui"
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="tabs-demo-username">Senha</Label>
                  <Input
                    type="password"
                    id="tabs-demo-username"
                    placeholder="Coloque sua senha aqui"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit">Login</Button>
              </CardFooter>
            </Card>
          </TabsContent>
          <TabsContent value="Register">
            <Card>
              <CardHeader>
                <CardTitle>Cadastro</CardTitle>
                <CardDescription>
                  Crie sua conta para começar a usar a plataforma.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="tabs-demo-current">Nome de Usuário</Label>
                  <Input
                    id="tabs-demo-current"
                    type="password"
                    placeholder="Coloque seu nome de usuário aqui"
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="tabs-demo-new">Senha</Label>
                  <Input
                    id="tabs-demo-new"
                    type="password"
                    placeholder="Coloque sua senha aqui"
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="tabs-demo-new">Confirmar Senha</Label>
                  <Input
                    id="tabs-demo-new"
                    type="password"
                    placeholder="Confirme sua senha aqui"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button>Cadastre-se</Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </form>
  );
}
